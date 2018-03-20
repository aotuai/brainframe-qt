import os
import sys

from PyQt5.QtWidgets import QApplication

from visionapp import api, MainWindow

if __name__ == '__main__':

    # Monkeypatch the api to be an instantiated object
    api.api = api.API("localhost", 80)

    # Ensure that all relative paths are correct
    os.chdir(os.path.dirname(__file__) + "/visionapp/client")

    app = QApplication(sys.argv)
    window = MainWindow()

    app.exec_()
