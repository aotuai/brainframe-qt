from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QLabel
from PyQt5.uic import loadUi

from brainframe.client.ui.dialogs.capsule_configuration import capsule_utils
from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths


class PluginListItem(QLabel):

    def __init__(self, name, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.capsule_list_item_ui, self)

        self.plugin_name = name
        self.setText(capsule_utils.pretty_snakecase(name))
