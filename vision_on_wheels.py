from argparse import ArgumentParser
from requests.exceptions import ConnectionError
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from visionapp.client import api, MainWindow, SplashScreen
from visionapp.client.ui.resources.paths import image_paths

# CLI Arguments
parser = ArgumentParser(description="This runs the client VisionApp")
parser.add_argument("-a", "--api-url", type=str,
                    default="http://localhost:8000",
                    help="The URL that the server is currently running on. "
                         "This can be localhost, or a local IP, or a remote"
                         " IP depending on your setup.")
args = parser.parse_args()

# Monkeypatch the api to be an instantiated object
api.__dict__['api'] = api.API(args.api_url)

# Run the UI
app = QApplication(sys.argv)
app.setWindowIcon(QIcon(str(image_paths.application_icon)))

with SplashScreen() as splash_screen:

    splash_screen.showMessage("Connection to server unsuccessful. Retrying")

    while True:

        try:
            # Set all stream analysis as "active" here, since there is currently
            # no # way to in the UI
            configs = api.api.get_stream_configurations()
        except ConnectionError:
            # Server not started yet
            app.processEvents()
            continue
        splash_screen.showMessage("Successfully connected to server. "
                                  "Starting UI")
        for config in configs:
            success = api.api.start_analyzing(config.id)

        main_window = MainWindow()
        main_window.show()
        splash_screen.finish(main_window)

        break

app.exec_()

# Close API threads
api.api.close()
