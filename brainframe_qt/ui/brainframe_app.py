import sys
import typing
from typing import List, Optional

import requests
from PyQt5.QtCore import QLocale, QMetaObject, QThread, QTranslator, Q_ARG, Qt, \
    pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox

import brainframe
from brainframe.api import bf_codecs, bf_errors
from brainframe.api.bf_errors import BaseAPIError
from brainframe.client.api_utils import api
from brainframe.client.ui import LicenseAgreement, MainWindow, SplashScreen
from brainframe.client.ui.dialogs import StandardError, VersionMismatch
# noinspection PyUnresolvedReferences
from brainframe.client.ui.resources import QTAsyncWorker, qt_resources, \
    settings
from brainframe.client.ui.resources.paths import text_paths
from brainframe.shared.gstreamer import gobject_init
from brainframe.shared.secret import decrypt


class BrainFrameApplication(QApplication):
    def __init__(self, argv: Optional[List] = ()):
        super().__init__(argv or [])

        self.splash_screen = typing.cast(SplashScreen, None)

        # noinspection PyUnresolvedReferences
        self.aboutToQuit.connect(self._shutdown)

        self.setWindowIcon(QIcon(":/app_icon_png"))
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
                QMessageBox.warning(None, title, message)

        else:
            self.installTranslator(translator)

    def exec(self):

        # Show splash screen while waiting for server connection
        with SplashScreen() as self.splash_screen:
            self._connect_to_server()
            self._verify_version_match()

            message = self.tr("Successfully connected to server. Starting UI")
            self.splash_screen.showMessage(message)

            main_window = MainWindow()
            self.splash_screen.finish(main_window)
            main_window.show()

        super().exec()

    @pyqtSlot(object, object, object, bool)
    def _handle_error(self, exc_type, exc_obj, exc_tb, other_thread=False):
        """Shows a dialog when an error occurs"""

        # Check if exception occurred in the UI thread
        if QThread.currentThread() is self.thread():

            # Close the client if the exception was thrown in another thread,
            # or if it was not an BaseAPIError
            close_client = other_thread \
                           or not isinstance(exc_obj, BaseAPIError)

            StandardError.show_error(exc_type, exc_obj, exc_tb, close_client)
        else:
            # Call this function again, but from the correct (UI) thread.
            # If a QWidget (the StandardError dialog) is used from another
            # thread we WILL segfault. This is undesirable
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

    # noinspection PyMethodMayBeStatic
    def _init_server_settings(self):
        api.set_url(settings.server_url.val())

        username = settings.server_username.val()

        if username:
            password = decrypt(settings.server_password.val())
            api.set_credentials((username, password))

    # noinspection PyMethodMayBeStatic
    def _shutdown(self):
        api.close()
        gobject_init.close()

    def _verify_license(self):
        # Ensure that user has accepted license agreement.
        # Otherwise close program
        if not LicenseAgreement.get_agreement(parent=None):
            sys.exit(self.tr("Program Closing: License Not Accepted"))

    def _connect_to_server(self):

        server_visible = False
        while not server_visible:

            message = self.tr("Attempting to communicate with server at {url}")
            f_message = message.format(url=settings.server_url.val())
            self.splash_screen.showMessage(f_message)

            self._wait_for_server()
            server_visible = True

            message = self.tr("Connected to server. Validating license")
            self.splash_screen.showMessage(message)

            connected = False
            while not connected:
                try:
                    self._wait_for_valid_license()
                except (ConnectionError, ConnectionRefusedError,
                        bf_errors.UnauthorizedError,
                        requests.exceptions.ReadTimeout):
                    # Server address change or disappeared for whatever reason
                    # Go back to waiting for server
                    server_visible = False
                else:
                    # Successfully connected
                    connected = True

    def _wait_for_server(self):
        worker = QTAsyncWorker(self, api.wait_for_server_initialization)
        worker.start()
        self._wait_for_event(worker.finished_event)

    def _wait_for_valid_license(self):
        license_valid = False
        while not license_valid:
            def on_error(exc: BaseException):
                raise exc

            worker = QTAsyncWorker(self, api.get_license_info,
                                   on_error=on_error)
            worker.start()
            self._wait_for_event(worker.finished_event)

            # noinspection PyTypeHints
            worker.data: bf_codecs.LicenseInfo
            if worker.data.state is bf_codecs.LicenseState.VALID:
                license_valid = True
                message = self.tr("Successfully connected to server")
            elif worker.data.state is bf_codecs.LicenseState.EXPIRED:
                message = self.tr("License is expired. Please upload a new "
                                  "one")
            elif worker.data.state is bf_codecs.LicenseState.INVALID:
                message = self.tr("Server holds an invalid license. Please "
                                  "upload a new one")
            elif worker.data.state is bf_codecs.LicenseState.MISSING:
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
        if version != brainframe.__version__:
            dialog = VersionMismatch(
                server_version=version,
                client_version=brainframe.__version__)
            dialog.exec_()

    def _wait_for_event(self, event):
        """Runs the Qt event loop while waiting on an event to be triggered."""
        while not event.wait(.1):
            self.processEvents()

    # Handle all exceptions using a graphical handler
    # https://stackoverflow.com/a/41921291/8134178
    # noinspection PyUnresolvedReferences
    sys.excepthook = _handle_error_.__func__
