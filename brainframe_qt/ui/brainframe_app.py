import logging
import typing
import sys
from traceback import TracebackException
from typing import List, Optional

from PyQt5.QtCore import QMetaObject, QThread, Q_ARG, Qt, pyqtSlot, QDeadlineTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget

from brainframe.api import bf_errors
from gstly import gobject_init

import brainframe_qt
from brainframe_qt.api_utils import api
from brainframe_qt.api_utils.connection_manager import ConnectionManager
from brainframe_qt.ui import EULADialog, MainWindow, SplashScreen
from brainframe_qt.ui.resources import QTAsyncWorker, qt_resources
from brainframe_qt.ui.resources.config import ServerSettings
from brainframe_qt.ui.resources.i18n.translator import BrainFrameTranslator
from brainframe_qt.ui.resources.ui_elements.widgets.dialogs import BrainFrameMessage


class BrainFrameApplication(QApplication):
    def __init__(self, argv: Optional[List] = ()):
        super().__init__(argv or [])
        self.server_config = ServerSettings()

        self.connection_manager = ConnectionManager(parent=self)
        self.splash_screen: SplashScreen = SplashScreen()
        self.main_window: Optional[MainWindow] = None

        self.translator = self._init_translator()

        self._init_style()
        self._init_signals()

        self._init_config()
        gobject_init.start(start_main_loop=False)

    def _init_signals(self) -> None:
        self.aboutToQuit.connect(self._shutdown)
        self.connection_manager.connection_state_changed.connect(
            self._on_connection_state_change
        )

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

        # Check if exception occurred in the UI thread
        if QThread.currentThread() is self.thread():

            title = self.tr("Error")
            description = self.tr("An exception has occurred")
            buttons = BrainFrameMessage.PresetButtons.EXCEPTION
            traceback_exc = TracebackException(exc_type, exc_obj, exc_tb)
            close_client = False

            # Close the client if the exception was thrown in another thread
            if other_thread:
                close_client = True
            if not isinstance(exc_obj, bf_errors.BaseAPIError):
                close_client = True

            if isinstance(exc_obj, bf_errors.ServerNotReadyError):
                description = self.tr(
                    "An unhandled exception occurred while communicating with "
                    "the BrainFrame server")
            else:
                description += self.tr(". The client must be closed.")

            if close_client:
                buttons &= ~BrainFrameMessage.PresetButtons.CLOSE_CLIENT
                buttons |= BrainFrameMessage.PresetButtons.OK

            # Log exception as well as show it to user
            log_func = logging.critical if close_client else logging.error
            exc_str = "".join(traceback_exc.format()).rstrip()
            log_func(exc_str)

            BrainFrameMessage.exception(
                parent=typing.cast(QWidget, None),  # No parent
                title=title,
                description=description,
                traceback=traceback_exc,
                buttons=buttons
            ).exec()

        else:
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
        return QApplication.instance()._handle_error(*args)

    def _init_config(self):
        self.setOrganizationDomain('aotu.ai')

    # noinspection PyMethodMayBeStatic
    def _shutdown(self):
        api.close()
        gobject_init.close()

        self.connection_manager.requestInterruption()
        self.connection_manager.wait(QDeadlineTimer(5))  # seconds
        self.connection_manager.terminate()

    def _start_ui(self):
        self.splash_screen.close()

        self.verify_version_match()

        self.main_window = MainWindow()
        self.main_window.show()

    def _verify_eula(self):
        # Ensure that user has accepted license agreement.
        # Otherwise close program
        if not EULADialog.get_agreement(parent=None):
            sys.exit(self.tr("Program Closing: License Not Accepted"))

    def verify_version_match(self):
        worker = QTAsyncWorker(self, api.version)
        worker.start()
        self._wait_for_event(worker.finished_event)

        version = worker.data
        if version != brainframe_qt.__version__:
            title = self.tr("Version Mismatch")
            message = self.tr(
                "The server is using version {server_version} but this client "
                "is on version {client_version}. Please download the matching "
                "version of the client at {download_url}.")
            message = message.format(
                server_version=version,
                client_version=brainframe_qt.__version__,
                download_url="aotu.ai/docs/downloads/")

            dialog = BrainFrameMessage.critical(
                parent=typing.cast(QWidget, None),
                title=title,
                text=message
            )

            dialog.setTextInteractionFlags(Qt.TextSelectableByMouse)

            dialog.exec()

    def _wait_for_event(self, event):
        """Runs the Qt event loop while waiting on an event to be triggered."""
        while not event.wait(.1):
            self.processEvents()

    # Handle all exceptions using a graphical handler
    # https://stackoverflow.com/a/41921291/8134178
    # noinspection PyUnresolvedReferences
    sys.excepthook = _handle_error_.__func__


# Import has side effects
_ = qt_resources
