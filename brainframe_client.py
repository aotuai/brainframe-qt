import logging
logging.getLogger().setLevel(logging.INFO)

# Import hack for LGPL compliance. This runs stuff on import
# noinspection PyUnresolvedReferences
from brainframe.shared import custom_libraries_lgpl

from argparse import ArgumentParser
from time import sleep
import signal
import sys
import os

from requests.exceptions import ConnectionError
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from brainframe.client.api import api
from brainframe.client.ui import MainWindow, SplashScreen, LicenseAgreement
from brainframe.client.ui.resources.paths import image_paths
from brainframe.client.api.api_errors import StreamNotOpenedError


def parse_args():
    parser = ArgumentParser(description="This runs the BrainFrame client")
    parser.add_argument("-a", "--api-url", type=str,
                        default="http://localhost:8000",
                        help="The URL that the server is currently running on. "
                             "This can be localhost, or a local IP, or a "
                             "remote IP depending on your setup.")
    parser.add_argument("--skip-frames", action="store_true",
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
    if args.skip_frames:
        logging.warning("Frames will be skipped to improve performance")
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "skip_frame;nonkey"

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
                # Set all stream analysis as "active" here, since there is
                # currently no way to in the UI
                configs = api.get_stream_configurations()
            except ConnectionError:
                # Server not started yet
                app.processEvents()

                # Prevent a busy loop while splash screen is open
                sleep(.1)
                continue

            splash_screen.showMessage("Successfully connected to server. "
                                      "Starting UI")
            for config in configs:
                try:
                    success = api.start_analyzing(config.id)
                except StreamNotOpenedError:
                    logging.error(f"Stream {config.name} is not open so "
                                  f"analysis did not start")

            main_window = MainWindow()
            main_window.show()
            splash_screen.finish(main_window)

            break

    app.exec_()

    # Close API threads
    api.close()
