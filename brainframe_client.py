# Import hack for LGPL compliance. This runs stuff on import
# noinspection PyUnresolvedReferences
from brainframe.shared import preimport_hooks

import faulthandler
import sys
from time import sleep

from requests.exceptions import ConnectionError
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from brainframe.client.api import api
from brainframe.client.api import api_errors
from brainframe.client.ui import MainWindow, SplashScreen, LicenseAgreement
from brainframe.client.ui.resources import settings
from brainframe.client.ui.resources.paths import image_paths
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

    # Ensure that user has accepted license agreement. Otherwise close program
    if not LicenseAgreement.get_agreement():
        sys.exit("Program Closing: License Not Accepted")

    gobject_init.start()

    init_server_settings()

    # Show splash screen while waiting for server connection
    with SplashScreen() as splash_screen:

        while True:
            try:
                splash_screen.showMessage(f"Attempting to connect to server "
                                          f"at {settings.server_url.val()}")
                api.version()
            except (ConnectionError, ConnectionRefusedError,
                    api_errors.UnauthorizedError):
                # Server not started yet
                app.processEvents()

                # Prevent a busy loop while splash screen is open
                sleep(.1)
                continue

            splash_screen.showMessage("Successfully connected to server. "
                                      "Starting UI")

            main_window = MainWindow()
            main_window.show()
            splash_screen.finish(main_window)

            break

    app.exec_()

    # Close API threads
    api.close()

    gobject_init.close()


def init_server_settings():
    api.set_url(settings.server_url.val())

    username = settings.server_username.val()

    if username:
        password = decrypt(settings.server_password.val())
        api.set_credentials((username, password))


if __name__ == '__main__':
    main()
