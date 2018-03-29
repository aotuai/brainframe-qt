import os
import sys

from PyQt5.QtWidgets import QApplication

from visionapp.client import api, MainWindow


# Monkeypatch the api to be an instantiated object
api.__dict__['api'] = api.API("http://localhost", 8000)

# Ensure that all relative paths are correct
os.chdir(os.path.dirname(__file__))

app = QApplication(sys.argv)
window = MainWindow()

app.exec_()

api.api.close()
