import logging
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtNetwork import QHostAddress
from PyQt5.QtNetworkAuth import QOAuthHttpServerReplyHandler

from brainframe_qt.util.oauth.base import AuthTokenResponse
from brainframe_qt.util.oauth.error import OAuthError, UnknownOAuthError


class PKCEReplyHandler(QOAuthHttpServerReplyHandler):
    ready = pyqtSignal()
    """Emitted when the ReplyHandler is ready for connections"""
    completed = pyqtSignal(AuthTokenResponse)
    """Emitted when the ReplyHandler has received an Authorization Code"""
    error = pyqtSignal(OAuthError)

    class UnknownCallbackError(UnknownOAuthError):
        def __init__(self, error: str, description: Optional[str]):
            self.error = error
            self.description = description

    class MissingCodeData(OAuthError):
        """Callback was called without providing `code` data"""

    class MissingStateData(OAuthError):
        """Callback was called without providing `state` data"""

    _PORTS = [21849, 32047, 31415]

    def __init__(self, *, parent: QObject):
        super().__init__(parent=parent)

        self.close()  # Constructor starts at a useless address/port

        self._init_signals()

    def _init_signals(self) -> None:
        self.callbackReceived.connect(self._on_callback_received)

    def start(self) -> None:
        """Start listening. Continue listening if not already listening"""
        if not self.isListening():
            for port in self._PORTS:
                logging.debug(f"PKCEReplyHandler attempting to listen at localhost:{port}")
                if self.listen(address=QHostAddress.LocalHost, port=port):
                    break

            else:
                logging.error("Unable to start PKCEReplyHandler on any configured port")
                return

        logging.debug(f"PKCEReplyHandler listening at localhost:{self.port()}")
        self.ready.emit()

    def _on_callback_received(self, values: dict) -> None:
        logging.debug(f"Callback received data: {values}")

        if not values:
            # Ignore empty requests
            return

        error: Optional[OAuthError] = None
        if "error" in values:
            error_type = values["error"]
            error_message = values.get("error_description")
            error = self.UnknownCallbackError(error_type, error_message)
        elif "code" not in values:
            error = self.MissingCodeData()
        elif "state" not in values:
            error = self.MissingStateData()

        if error is not None:
            self.error.emit(error)
            return

        auth_response = AuthTokenResponse(
            authorization_code=values["code"],
            state=values["state"]
        )

        self.completed.emit(auth_response)
