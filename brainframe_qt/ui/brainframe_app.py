import logging
import sys
import typing
from traceback import TracebackException

from PyQt5.QtCore import QLocale, QMetaObject, QThread, QTranslator, Q_ARG, \
    Qt, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QApplication
from brainframe.api import bf_codecs, bf_errors
from gstly import gobject_init

import brainframe_qt
from brainframe_qt.api_utils import api
from brainframe_qt.extensions.loader import ExtensionLoader
from brainframe_qt.ui import EULADialog, MainWindow, SplashScreen
# noinspection PyUnresolvedReferences
from brainframe_qt.ui.resources import QTAsyncWorker, qt_resources
from brainframe_qt.ui.resources.config import ServerSettings
from brainframe_qt.ui.resources.paths import text_paths
from brainframe_qt.ui.resources.ui_elements.applications import \
    SingletonApplication
from brainframe_qt.ui.resources.ui_elements.widgets.dialogs import BrainFrameMessage
from brainframe_qt.util.secret import decrypt


class BrainFrameApplication(SingletonApplication):
    def __init__(self):
        super().__init__(internal_name="brainframe-qt")
        self.server_config = ServerSettings()

        self.splash_screen = typing.cast(SplashScreen, None)

        self.aboutToQuit.connect(self._shutdown)

        self.setWindowIcon(QIcon(":/icons/window_icon"))
        self.setOrganizationDomain('aotu.ai')

        self._init_translator()

        gobject_init.start(start_main_loop=False)

        self._init_server_settings()

    def _init_translator(self):
        locale = QLocale.system()
        translator = QTranslator(self)
        i18n_dir = str(text_paths.i18n_dir)
        if not translator.load(locale, "brainframe", '_', i18n_dir):

            if locale.language() != locale.English:
                # TODO: Find a better way that doesn't rely on a _list of
                #  preferences_. If, say, zh_BA (which isn't a thing) is
                #  used, locale.name() returns zh_CN (which _is_ a real
                #  language). If there is no `zh` language, we want to throw
                #  a warning with zh_BA specified, not zh_CN. We settle for
                #  locale.uiLanguages() because it returns ['zh_BA']. Not
                #  sure if it might have other entries under some conditions.
                locale_str = locale.uiLanguages()[0]

                title = "Error loading language files"
                message = (f"Unable to load translation file for "
                           f"[{locale_str}] locale. Using English as a "
                           f"fallback.")

                # noinspection PyTypeChecker
                BrainFrameMessage.warning(
                    parent=None,
                    title=title,
                    warning=message
                ).exec()

        else:
            self.installTranslator(translator)

    def exec(self):

        self._verify_eula()

        # Show splash screen while waiting for server connection
        with SplashScreen() as self.splash_screen:
            self._connect_to_server()
            self._verify_version_match()

            message = self.tr("Successfully connected to server. Starting UI")
            self.splash_screen.showMessage(message)

            ExtensionLoader().load_extensions()

            self.main_window = MainWindow()
            self.main_window.show()

            self.splash_screen.finish(self.main_window)

        super().exec()

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

        if exc_type not in [
            self.BaseMessagingError,
        ]:
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

    # noinspection PyMethodMayBeStatic
    def _init_server_settings(self):
        api.set_url(self.server_config.server_url)

        username = self.server_config.server_username
        password = self.server_config.server_password

        if username and password:
            password = decrypt(password)
            api.set_credentials((username, password))

    # noinspection PyMethodMayBeStatic
    def _shutdown(self):
        api.close()
        gobject_init.close()

    def _verify_eula(self):
        # Ensure that user has accepted license agreement.
        # Otherwise close program
        if not EULADialog.get_agreement(parent=None):
            sys.exit(self.tr("Program Closing: License Not Accepted"))

    def _connect_to_server(self):

        server_visible = False
        while not server_visible:

            message = self.tr("Attempting to communicate with server at {url}")
            f_message = message.format(url=self.server_config.server_url)
            self.splash_screen.showMessage(f_message)

            self._wait_for_server()
            server_visible = True

            message = self.tr("Connected to server. Validating license")
            self.splash_screen.showMessage(message)

            connected = False
            while not connected:
                try:
                    self._wait_for_valid_license()
                except (bf_errors.ServerNotReadyError,
                        bf_errors.UnauthorizedError):
                    # Server address change or disappeared for whatever reason
                    # Go back to waiting for server
                    server_visible = False
                else:
                    # Successfully connected
                    connected = True

    def _wait_for_server(self):

        def on_error(_):
            # Do nothing. We'll handle the error using worker.err
            pass

        while True:
            worker = QTAsyncWorker(self, api.wait_for_server_initialization,
                                   on_error=on_error)
            worker.start()
            self._wait_for_event(worker.finished_event)

            # Connection successful
            if worker.err is None:
                break

            # Ignore standard communication errors
            elif not isinstance(worker.err, bf_errors.ServerNotReadyError):
                raise worker.err

    def _wait_for_valid_license(self):
        license_valid = False
        while not license_valid:
            def on_error(_):
                # Do nothing. We'll handle the error using worker.err
                pass

            worker = QTAsyncWorker(self, api.get_license_info,
                                   on_error=on_error)
            worker.start()
            self._wait_for_event(worker.finished_event)
            if worker.err is not None:
                raise worker.err

            # noinspection PyTypeHints
            worker.data: bf_codecs.LicenseInfo
            if worker.data.state is bf_codecs.LicenseInfo.State.VALID:
                license_valid = True
                message = self.tr("Successfully connected to server")
            elif worker.data.state is bf_codecs.LicenseInfo.State.EXPIRED:
                message = self.tr("License is expired. Please upload a new "
                                  "one")
            elif worker.data.state is bf_codecs.LicenseInfo.State.INVALID:
                message = self.tr("Invalid License. Does the server have a "
                                  "connection to the internet?")
            elif worker.data.state is bf_codecs.LicenseInfo.State.MISSING:
                message = self.tr("No license exists on the server. Please "
                                  "upload one")
            else:
                message = self.tr("Unknown issue with license. Contact Aotu")
            self.splash_screen.showMessage(message)

    def _verify_version_match(self):
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
