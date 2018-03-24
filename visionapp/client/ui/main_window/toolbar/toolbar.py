from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from visionapp.client.ui.resources.paths import qt_ui_paths


class Toolbar(QWidget):

    def __init__(self, parent):

        super().__init__(parent)

        loadUi(qt_ui_paths.toolbar_ui, self)
