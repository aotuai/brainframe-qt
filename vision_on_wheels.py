import os
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        loadUi("ui/main_window/main.ui", self).show()

        print(dir(self))


if __name__ == '__main__':

    os.chdir(os.path.dirname(__file__) + "/visionapp")

    app = QApplication(sys.argv)
    window = MainWindow()

    app.exec_()
