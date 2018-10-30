from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QLabel
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths


class PluginListItem(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.plugin_list_item_ui, self)
