from typing import Dict

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths


class PluginConfigDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.plugin_config_dialog_ui, self)

    @classmethod
    def show_dialog(cls):
        dialog = cls()
        dialog.exec_()