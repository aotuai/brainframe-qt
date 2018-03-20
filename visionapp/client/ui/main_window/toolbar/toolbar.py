from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

import client_paths


class Toolbar(QWidget):

    def __init__(self, parent):

        super().__init__(parent)

        loadUi(client_paths.toolbar_ui, self)
