from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from visionapp.client.ui.resources.paths import qt_ui_paths


class AlertLog(QWidget):

    def __init__(self, parent):

        super().__init__(parent)

        loadUi(qt_ui_paths.alert_log_ui, self)
