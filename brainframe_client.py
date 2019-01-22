import logging
import os

# Import hack for LGPL compliance. This runs stuff on import
# noinspection PyUnresolvedReferences
from brainframe.shared import custom_libraries_lgpl

from argparse import ArgumentParser
from time import sleep
import signal
import sys

from requests.exceptions import ConnectionError
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from brainframe.shared.ffmpeg_options import set_opencv_ffmpeg_capture_options
from brainframe.client.api import api
from brainframe.client.ui import (
    MainWindow,
    SplashScreen,
    LicenseAgreement,
    VideoConfiguration
)
from brainframe.client.ui.resources.paths import image_paths
from brainframe.client.api.api_errors import StreamNotOpenedError
from brainframe.shared import environment


default_log_level = "INFO"
if environment.in_production():
    # Be less verbose in production
    default_log_level = "WARN"
logging.basicConfig(level=os.environ.get("LOGLEVEL", default_log_level))


def parse_args():
    parser = ArgumentParser(description="This runs the BrainFrame client")
    parser.add_argument("-a", "--api-url", type=str,
                        default="http://localhost:8000",
                        help="The URL that the server is currently running "
                             "on. This can be localhost, or a local IP, or a "
                             "remote IP depending on your setup.")
    parser.add_argument("--skip-frames", action="store_true", default=False,
                        help="Configures all streams to skip intermediate "
                             "frames and process only keyframes. This is "
                             "useful when many streams are being processed.")
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    # Handle Keyboard Interrupt
    signal.signal(signal.SIGINT, lambda _signal, _frame: sys.exit("Exiting"))

    args = parse_args()

    # Set the frame skipping environment variable if necessary
    set_opencv_ffmpeg_capture_options(
        skip_frames=args.skip_frames)

    # Set the API url
    api.set_url(args.api_url)

    # Run the UI
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(str(image_paths.application_icon)))
    app.setOrganizationName('dilili-labs')
    app.setOrganizationDomain('dilililabs.com')
    app.setApplicationName('brainframe')

    # Ensure that user has accepted license agreement. Otherwise close program
    if not LicenseAgreement.get_agreement():
        sys.exit("Program Closing: License Not Accepted")

    # Show splash screen while waiting for server connection
    with SplashScreen() as splash_screen:
        splash_screen.showMessage("Attempting to connect to server")

        while True:
            try:
                configs = api.get_stream_configurations()
            except ConnectionError:
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
