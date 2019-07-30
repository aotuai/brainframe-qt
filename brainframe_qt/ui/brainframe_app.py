import sys
from time import sleep
from typing import List, Optional

from requests.exceptions import ConnectionError

from PyQt5.QtCore import QLocale, QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox

from brainframe.client.api import api, api_errors
from brainframe.client.ui import MainWindow, SplashScreen, LicenseAgreement
from brainframe.client.ui.dialogs import StandardError
from brainframe.client.ui.resources import settings
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

        gobject_init.start()

        self._init_server_settings()

    def _init_translator(self):
        locale = QLocale.system()
        translator = QTranslator(self)
        i18n_dir = str(text_paths.i18n_dir)
        if not translator.load(locale, "brainframe", '_', i18n_dir):
            # TODO: Find a better way that doesn't rely on a _list of
            #  preferences_. If, say, zh_BA (which isn't a thing) is used,
            #  locale.name() returns zh_CN (which _is_ a real language). If
            #  there is no `zh` language, we want to throw a warning with
            #  zh_BA specified, not zh_CN. We settle for
            #  locale.uiLanguages() because it returns ['zh_BA']. Not sure if
            #  it might have other entries under some conditions.
            locale = locale.uiLanguages()[0]
            title = "Error loading language files"
            message = (f"Unable to load translation file for {locale} locale. "
                       f"Using English as a fallback.")

            # noinspection PyTypeChecker
            QMessageBox.warning(None, title, message)

            english_locale = QLocale(QLocale.English, QLocale.UnitedStates)
            if not translator.load(english_locale, "brainframe", '_',
                                   i18n_dir):
                raise RuntimeError("Unable to set locale to even en_US. "
                                   "Something is wrong")

        self.installTranslator(translator)

    def exec(self):

        # Show splash screen while waiting for server connection
        with SplashScreen() as splash_screen:

            message = self.tr("Attempting to connect to server at {}")

            while True:
                try:
                    f_message = message.format(settings.server_url.val())
                    splash_screen.showMessage(f_message)

                    # Test connection to server
                    api.version()
                except (ConnectionError, ConnectionRefusedError,
                        api_errors.UnauthorizedError):
                    # Server not started yet
                    self.processEvents()

                    # Prevent a busy loop while splash screen is open
                    sleep(.1)
                    continue

                message = self.tr("Successfully connected to server. "
                                  "Starting UI")
                splash_screen.showMessage(message)

                main_window = MainWindow()
                splash_screen.finish(main_window)
                main_window.show()

                break

        super().exec()

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

    sys.excepthook = StandardError.show_error
