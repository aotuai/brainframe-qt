from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi


class Toolbar(QWidget):

    def __init__(self, parent):

        super().__init__(parent)

        loadUi("ui/main_window/toolbar/toolbar.ui", self)