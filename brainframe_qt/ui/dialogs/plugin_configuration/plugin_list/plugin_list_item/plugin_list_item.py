from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QLabel
from PyQt5.uic import loadUi

from brainframe.client.ui.dialogs.plugin_configuration import plugin_utils
from brainframe.client.api_helpers import api
from brainframe.client.ui.resources.paths import qt_ui_paths


class PluginListItem(QLabel):

    def __init__(self, name, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.plugin_list_item_ui, self)

        self.plugin_name = name
        self.setText(plugin_utils.pretty_snakecase(name))
