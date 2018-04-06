import os
import sys
from argparse import ArgumentParser

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from visionapp.client import api, MainWindow
from visionapp.client.ui.resources.paths import image_paths

# CLI Arguments
parser = ArgumentParser(description="This runs the client VisionApp")
parser.add_argument("-a", "--api-url", type=str, default="http://localhost:8000",
                    help="The URL that the server is currently running on. "
                         "This can be localhost, or a local IP, or a remote"
                         " IP depending on your setup.")
args = parser.parse_args()


# Monkeypatch the api to be an instantiated object
api.__dict__['api'] = api.API(args.api_url)

# Set all stream analysis as "active" here, since there's no way to in the UI
configs = api.api.get_stream_configurations()
for config in configs:
    success = api.api.start_analyzing(config.id)

# Run the UI
app = QApplication(sys.argv)
app.setWindowIcon(QIcon(str(image_paths.application_icon)))
window = MainWindow()
app.exec_()

# Close API threads
api.api.close()
