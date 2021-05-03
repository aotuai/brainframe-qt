from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple

from PyQt5.QtCore import pyqtSignal, QObject, QThread

from brainframe.api import bf_errors, bf_codecs

from brainframe_qt.api_utils import api
from brainframe_qt.ui.resources.config import ServerSettings
from brainframe_qt.util.secret import decrypt


class ConnectionManager(QThread):
    _CONNECTED_SLEEP_TIME = 100  # ms
    _CONNECT_TIMEOUT = 5  # s

    connection_state_changed = pyqtSignal(object)
    license_state_changed = pyqtSignal(bf_codecs.LicenseInfo.State)

    connection_error = pyqtSignal(Exception)

    class ConnectionState(Enum):
        UNCONFIGURED = auto()
        """Credentials not accessed, or in need of update"""
        UNCONNECTED = auto()
        """No communication with server yet"""
        LICENSE_UNVALIDATED = auto()
        """License not yet validated"""
        LICENSE_EXPIRED = auto()
        """Current license is expired"""
        LICENSE_INVALID = auto()
        """Current license invalid"""
        LICENSE_MISSING = auto()
        """Current license is missing"""
        CONNECTED = auto()
        """Connected to server and ready to use API"""
        RUNTIME_ERROR = auto()

    def __init__(self, *, parent: QObject):
        super().__init__(parent=parent)

        self._connection_state = self.ConnectionState.UNCONFIGURED
        self._connection_configuration: Optional[ConnectionConfiguration] = None

        self.server_settings = ServerSettings()

        self._init_signals()

    def run(self) -> None:
        while not self.isInterruptionRequested():
            if self.connection_state is self.ConnectionState.CONNECTED:
                QThread.msleep(self._CONNECTED_SLEEP_TIME)
            elif self.connection_state is self.ConnectionState.UNCONFIGURED:
                self._get_configuration()
            elif self.connection_state is self.ConnectionState.UNCONNECTED:
                self._communicate_with_server()
            elif self.connection_state in [
                self.ConnectionState.LICENSE_UNVALIDATED,
                self.ConnectionState.LICENSE_EXPIRED,
                self.ConnectionState.LICENSE_INVALID,
                self.ConnectionState.LICENSE_MISSING
            ]:
                self._validate_license()
            elif self.connection_state is self.ConnectionState.RUNTIME_ERROR:
                QThread.msleep(self._CONNECTED_SLEEP_TIME)
            else:
                exc = RuntimeError(f"Unknown ConnectionState {self.connection_state}")
                self._handle_error(exc)

    def _init_signals(self) -> None:
        self.server_settings.value_changed.connect(self._handle_settings_change)

    @property
    def connection_state(self) -> ConnectionState:
        return self._connection_state

    @connection_state.setter
    def connection_state(self, connection_state: ConnectionState) -> None:
        prev_state = self._connection_state

        self._connection_state = connection_state

        if prev_state != connection_state:
            self.connection_state_changed.emit(connection_state)

    def invalidate_config(self) -> None:
        """Force the ConnectionManager to restart the authentication process"""
        self.connection_state = self.ConnectionState.UNCONFIGURED

    def _get_configuration(self) -> None:
        url = self.server_settings.server_url
        username = self.server_settings.server_username
        password = self.server_settings.server_password

        if username and password:
            password = decrypt(password)

        self._connection_configuration = ConnectionConfiguration(
            server_url=url,
            server_username=username,
            server_password=password,
        )
        api.set_url(self._connection_configuration.server_url)
        api.set_credentials(self._connection_configuration.credentials)

        self.connection_state = self.ConnectionState.UNCONNECTED

    def _communicate_with_server(self) -> None:
        try:
            api.wait_for_server_initialization(self._CONNECT_TIMEOUT)
        except (TimeoutError, bf_errors.ServerNotReadyError):
            self.connection_state = self.ConnectionState.UNCONNECTED
        else:
            self.connection_state = self.ConnectionState.LICENSE_UNVALIDATED

    def _validate_license(self) -> None:
        try:
            license_info = api.get_license_info()
        except (bf_errors.ServerNotReadyError, bf_errors.UnauthorizedError):
            self.connection_state = self.ConnectionState.UNCONNECTED
        else:
            if license_info.state is license_info.State.VALID:
                self.connection_state = self.ConnectionState.CONNECTED
            elif license_info.state is license_info.State.EXPIRED:
                self.connection_state = self.ConnectionState.LICENSE_EXPIRED
            elif license_info.state is license_info.State.INVALID:
                self.connection_state = self.ConnectionState.LICENSE_INVALID
            elif license_info.state is license_info.State.MISSING:
                self.connection_state = self.ConnectionState.LICENSE_MISSING
            else:
                exc = RuntimeError(f"Unknown LicenseInfo.State {license_info.state}")
                self._handle_error(exc)

    def _handle_error(self, exc: Exception) -> None:
        self.connection_error.emit(exc)
        self.connection_state = self.ConnectionState.RUNTIME_ERROR

    def _handle_settings_change(self, _setting: str, _value: object):
        self.invalidate_config()


@dataclass
class ConnectionConfiguration:
    server_url: Optional[str]
    server_username: Optional[str]
    server_password: Optional[str]
    license: Optional[str] = None

    @property
    def credentials(self) -> Optional[Tuple[str, str]]:
        if self.server_username is None:
            return None

        # If we have a password w/ no username, we'll just treat it as no password
        password = self.server_password if self.server_password is not None else ""

        return self.server_username, password
