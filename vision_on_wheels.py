import os
import sys

from PyQt5.QtWidgets import QApplication

# TODO: Wrap this up in something nicer
from visionapp.client.ui.main import Main

if __name__ == '__main__':

    # Ensure that all relative paths are correct
    os.chdir(os.path.dirname(__file__) + "/visionapp")

    app = QApplication(sys.argv)
    window = Main()

    app.exec_()
