import logging
import typing
import sys
from traceback import TracebackException
from typing import Optional

from PyQt5.QtCore import QMetaObject, QThread, Q_ARG, Qt, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget

from brainframe.api import bf_errors
from gstly import gobject_init

import brainframe_qt
from brainframe_qt.api_utils import api
from brainframe_qt.api_utils.connection_manager import ConnectionManager
from brainframe_qt.extensions.loader import ExtensionLoader
from brainframe_qt.ui import EULADialog, MainWindow, SplashScreen
from brainframe_qt.ui.resources import qt_resources
from brainframe_qt.ui.resources.config import ServerSettings
from brainframe_qt.ui.resources.i18n.translator import BrainFrameTranslator
from brainframe_qt.ui.resources.links.documentation import DOWNLOADS_LINK
from brainframe_qt.ui.resources.ui_elements.applications import SingletonApplication
from brainframe_qt.ui.resources.ui_elements.widgets.dialogs import BrainFrameMessage


class BrainFrameApplication(SingletonApplication):
    def __init__(self):
        super().__init__(internal_name="brainframe-qt")
        self.server_config = ServerSettings()

        self.connection_manager = ConnectionManager(parent=self)
        self.splash_screen: SplashScreen = SplashScreen()
        self.main_window: Optional[MainWindow] = None

        self.translator = self._init_translator()

        self._init_style()
        self.__init_signals()

        self._init_config()
        gobject_init.start(start_main_loop=False)

    def __init_signals(self) -> None:
        self.aboutToQuit.connect(self._shutdown)
        self.connection_manager.connection_state_changed.connect(
            self._on_connection_state_change
        )

        # If the splashscreen is manually closed, we should just exit
        self.splash_screen.manually_closed.connect(self.quit)

    def _init_style(self) -> None:
        self.setWindowIcon(QIcon(":/icons/window_icon"))

    def _init_translator(self) -> BrainFrameTranslator:
        translator = BrainFrameTranslator()
        self.installTranslator(translator)

        return translator

    def exec(self):
        self._verify_eula()
        self.connection_manager.start()
        self.splash_screen.show()
        super().exec()

    def _check_server_version(self) -> None:
        server_version = api.version()

        server_split = server_version.split(".")
        client_split = brainframe_qt.__version__.split(".")

        if client_split[:2] != server_split[:2]:
            client_outdated = client_split[:2] < server_split[:2]
            self._handle_version_mismatch(server_version, client_outdated)

    def _on_connection_state_change(
        self, connection_state: ConnectionManager.ConnectionState
    ):
        if connection_state is ConnectionManager.ConnectionState.CONNECTED:
            message = self.tr("Successfully connected to server")
            self._start_ui()
        elif connection_state is ConnectionManager.ConnectionState.UNCONFIGURED:
            message = self.tr("Collecting server authentication configuration")
        elif connection_state is ConnectionManager.ConnectionState.UNCONNECTED:
            message = self.tr("Attempting to communicate with server at {url}")
            message = message.format(url=self.server_config.server_url)
        elif connection_state is ConnectionManager.ConnectionState.LICENSE_UNVALIDATED:
            message = self.tr("Connected to server. Validating license")
        elif connection_state is ConnectionManager.ConnectionState.LICENSE_EXPIRED:
            message = self.tr("License is expired. Please upload a new one")
        elif connection_state is ConnectionManager.ConnectionState.LICENSE_INVALID:
            message = self.tr(
                "Invalid License. Does the server have a connection to the internet?"
            )
        elif connection_state is ConnectionManager.ConnectionState.LICENSE_MISSING:
            message = self.tr("No license exists on the server. Please upload one")
        else:
            raise RuntimeError(f"Unknown ConnectionState {connection_state}")

        self.splash_screen.showMessage(message)

    @pyqtSlot(object, object, object, bool)
    def _handle_error(self, exc_type, exc_obj, exc_tb, other_thread=False):
        """Shows a dialog when an error occurs"""

        # Make sure the exception occurred in the UI thread
        if QThread.currentThread() is not self.thread():

            # Call this function again, but from the correct (UI) thread.
            # If a QWidget (the BrainFrameMessage in this case) is used from
            # another thread we WILL segfault. This is undesirable
            QMetaObject.invokeMethod(
                self, "_handle_error",
                Qt.BlockingQueuedConnection,
                Q_ARG("PyQt_PyObject", exc_type),
                Q_ARG("PyQt_PyObject", exc_obj),
                Q_ARG("PyQt_PyObject", exc_tb),

                # Note: other_thread is now set true
                Q_ARG("bool", True)
            )

            return

        traceback_exc = TracebackException(exc_type, exc_obj, exc_tb)

        if not issubclass(exc_type, self.BaseMessagingError):
            # Close the client if the exception was thrown in another thread
            need_close = other_thread
            self._handle_error_with_dialog(traceback_exc, need_close)

        self._handle_error_with_log(traceback_exc)

    @staticmethod
    def _handle_error_(*args):
        """Alright so this is kinda ugly but...

        1. QMetaObject.invokeMethod for some reason doesn't work with static
        methods
        2. sys.excepthook needs a static/unbound method
        3. I can't have both

        So what I do is use the convenient fact that QApplications are
        singletons. The static method simply calls the instance method of the
        QApplication
        """

        # noinspection PyProtectedMember
        return BrainFrameApplication.instance()._handle_error(*args)

    def _handle_error_with_dialog(
        self, traceback_exc: TracebackException, need_close: bool = False
    ) -> None:
        title = self.tr("Error")
        description = self.tr("An exception has occurred")
        buttons = BrainFrameMessage.PresetButtons.EXCEPTION

        if traceback_exc.exc_type is not bf_errors.BaseAPIError:
            need_close = True

        if traceback_exc.exc_type is bf_errors.ServerNotReadyError:
            description = self.tr(
                "An unhandled exception occurred while communicating with "
                "the BrainFrame server")
        else:
            description += self.tr(". The client must be closed.")

        if need_close:
            buttons &= ~BrainFrameMessage.PresetButtons.CLOSE_CLIENT
            buttons |= BrainFrameMessage.PresetButtons.OK

        BrainFrameMessage.exception(
            parent=typing.cast(QWidget, None),  # No parent
            title=title,
            description=description,
            traceback=traceback_exc,
            buttons=buttons
        ).exec()

    def _handle_error_with_log(
        self, traceback_exc: TracebackException, log_level: int = logging.ERROR
    ) -> None:
        exc_str = "".join(traceback_exc.format()).rstrip()
        logging.log(log_level, exc_str)

    def _init_config(self):
        self.setOrganizationDomain('aotu.ai')

    # noinspection PyMethodMayBeStatic
    def _shutdown(self):
        api.close()
        gobject_init.close()

        self.connection_manager.requestInterruption()
        self.connection_manager.wait(5000)  # milliseconds
        self.connection_manager.terminate()

    def _start_ui(self):
        # Start the client if not already started
        if not self.main_window:

            self._check_server_version()

            ExtensionLoader().load_extensions()

            self.main_window = MainWindow()
            self.main_window.show()

            self.splash_screen.finish(self.main_window)

    def _verify_eula(self):
        # Ensure that user has accepted license agreement.
        # Otherwise close program
        if not EULADialog.get_agreement(parent=None):
            sys.exit(self.tr("Program Closing: License Not Accepted"))

    def _handle_version_mismatch(
            self, server_version: str, client_outdated: bool
    ) -> None:
        title = self.tr("Version Mismatch")
        text = self.tr(
            "The server is using version {server_version} but this client is on "
            "version {client_version}.")
        subtext = self.tr(
            "For a stable experience, please "
            "<a href='{client_download_url}'>download</a> the latest {outdated} "
            "version."
        )
        outdated = self.tr("client") if client_outdated else self.tr("server")

        text = text.format(
            server_version=server_version,
            client_version=brainframe_qt.__version__,
        )
        subtext = subtext.format(
            client_download_url=DOWNLOADS_LINK,
            outdated=outdated,
        )

        dialog = BrainFrameMessage.warning(
            parent=typing.cast(QWidget, None),
            title=title,
            warning=text,
            subtext=subtext,
        )

        dialog.setTextInteractionFlags(Qt.TextSelectableByMouse)

        dialog.exec()

    # Handle all exceptions using a graphical handler
    # https://stackoverflow.com/a/41921291/8134178
    # noinspection PyUnresolvedReferences
    sys.excepthook = _handle_error_.__func__


# Import has side effects
_ = qt_resources
