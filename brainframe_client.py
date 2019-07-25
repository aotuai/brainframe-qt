# Import hack for LGPL compliance. This runs stuff on import
# noinspection PyUnresolvedReferences
from brainframe.shared import preimport_hooks

import faulthandler
from functools import partial
import sys
from time import sleep

from requests.exceptions import ConnectionError

from PyQt5.QtCore import QLocale, QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMessageBox

from brainframe.client.api import api
from brainframe.client.api import api_errors
from brainframe.client.ui import MainWindow, SplashScreen, LicenseAgreement
from brainframe.client.ui.resources import settings
from brainframe.client.ui.resources.paths import image_paths, text_paths
from brainframe.shared.gstreamer import gobject_init
from brainframe.shared import environment
from brainframe.shared.secret import decrypt


def main():
    faulthandler.enable()

    environment.set_up_environment()

    # Run the UI
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(str(image_paths.application_icon)))
    app.setOrganizationDomain('dilililabs.com')

    app.installTranslator(init_translator(app))

    # Ensure that user has accepted license agreement. Otherwise close program
    if not LicenseAgreement.get_agreement():
        sys.exit("Program Closing: License Not Accepted")

    gobject_init.start()

    init_server_settings()

    # Show splash screen while waiting for server connection
    with SplashScreen() as splash_screen:

        # Bind tr to use global context
        tr = partial(QApplication.translate, "@default")

        while True:
            try:
                message = (tr("Attempting to connect to server at") +
                           f" {settings.server_url.val()}")
                splash_screen.showMessage(message)
                api.version()
            except (ConnectionError, ConnectionRefusedError,
                    api_errors.UnauthorizedError):
                # Server not started yet
                app.processEvents()

                # Prevent a busy loop while splash screen is open
                sleep(.1)
                continue

            message = tr("Successfully connected to server. Starting UI")
            splash_screen.showMessage(message)

            main_window = MainWindow()
            main_window.show()
            splash_screen.finish(main_window)

            break

    app.exec_()

    # Close API threads
    api.close()

    gobject_init.close()


def init_translator(app):
    locale = QLocale.system()
    translator = QTranslator(app)
    i18n_dir = str(text_paths.i18n_dir)
    if not translator.load(locale, "brainframe", '_', i18n_dir):
        # TODO: Find a better way that doesn't rely on a _list of preferences_.
        #       If, say, zh_BA (which isn't a thing) is used, locale.name()
        #       returns zh_CN (which _is_ a real language). If there is no `zh`
        #       language, we want to throw a warning with zh_BA specified, not
        #       zh_CN. We settle for locale.uiLanguages() because it returns
        #       ['zh_BA']. Not sure if it might have other entries under some
        #       conditions.
        locale = locale.uiLanguages()[0]
        title = "Error loading language files"
        message = (f"Unable to load translation file for {locale} locale. "
                   f"Using English as a fallback.")

        # noinspection PyTypeChecker
        QMessageBox.warning(None, title, message)

        english_locale = QLocale(QLocale.English, QLocale.UnitedStates)
        if not translator.load(english_locale, "brainframe", '_', i18n_dir):
            raise RuntimeError("Unable to set locale to even en_US. "
                               "Something is wrong")

    app.installTranslator(translator)


def init_server_settings():
    api.set_url(settings.server_url.val())

    username = settings.server_username.val()

    if username:
        password = decrypt(settings.server_password.val())
        api.set_credentials((username, password))


if __name__ == '__main__':
    main()
