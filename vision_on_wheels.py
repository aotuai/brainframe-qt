import os
import sys

from PyQt5.QtWidgets import QApplication

# TODO: Wrap this up in something nicer
import api
from visionapp.client.ui.main_window.main_window import MainWindow

if __name__ == '__main__':

    api.api = api.API("localhost", 80)

    # Ensure that all relative paths are correct
    os.chdir(os.path.dirname(__file__) + "/visionapp/client")

    app = QApplication(sys.argv)
    window = MainWindow()

    app.exec_()
