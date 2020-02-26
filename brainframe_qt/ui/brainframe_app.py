import sys
from threading import Event
from typing import List, Optional
from queue import Queue

from PyQt5.QtCore import pyqtSlot, Qt, Q_ARG, QLocale, QMetaObject, QThread, \
    QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox

import brainframe
from brainframe.client.api import api, api_errors
from brainframe.client.ui import MainWindow, SplashScreen, LicenseAgreement
from brainframe.client.ui.dialogs import StandardError, VersionMismatch
from brainframe.client.ui.resources import QTAsyncWorker, settings
from brainframe.client.ui.resources.paths import image_paths, text_paths
from brainframe.shared.gstreamer import gobject_init
from brainframe.shared.secret import decrypt


class BrainFrameApplication(QApplication):
    def __init__(self, argv: Optional[List] = ()):
        super().__init__(argv or [])

        # noinspection PyUnresolvedReferences
        self.aboutToQuit.connect(self._shutdown)

        self.setWindowIcon(QIcon(str(image_paths.application_icon)))
        self.setOrganizationDomain('dilililabs.com')

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
        with SplashScreen() as splash_screen:
            message = self.tr("Attempting to connect to server at {}")
            f_message = message.format(settings.server_url.val())
            splash_screen.showMessage(f_message)

            worker = QTAsyncWorker(
                self, api.wait_for_server_initialization,
                callback=lambda _: None)
            worker.start()
            self._wait_for_event(worker.finished_event)

            version_queue = Queue(maxsize=1)

            worker = QTAsyncWorker(
                self, api.version,
                callback=lambda result: version_queue.put(result))
            worker.start()
            self._wait_for_event(worker.finished_event)

            version = version_queue.get()
            if version != brainframe.__version__:
                dialog = VersionMismatch(
                    server_version=version,
                    client_version=brainframe.__version__)
                dialog.exec_()

            message = self.tr("Successfully connected to server. Starting UI")
            splash_screen.showMessage(message)

            main_window = MainWindow()
            splash_screen.finish(main_window)
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
                           or not isinstance(exc_obj, api_errors.BaseAPIError)

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

    def _wait_for_event(self, event):
        """Runs the Qt event loop while waiting on an event to be triggered."""
        while not event.wait(.1):
            self.processEvents()

    # Handle all exceptions using a graphical handler
    # https://stackoverflow.com/a/41921291/8134178
    # noinspection PyUnresolvedReferences
    sys.excepthook = _handle_error_.__func__
