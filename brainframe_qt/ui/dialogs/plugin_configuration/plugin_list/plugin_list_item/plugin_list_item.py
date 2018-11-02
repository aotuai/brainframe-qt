from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QLabel
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths


class PluginListItem(QLabel):

    def __init__(self, name, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.plugin_list_item_ui, self)

        # Make a prettier version of the plugin name, for display purposes
        display_name = (name
                        .replace('_', ' ')
                        .replace('-', ' ')
                        .strip()
                        .title())
        display_name = ''.join([c for c in display_name
                                if c.isalnum() or c == ' '])

        self.plugin_name = name
        self.setText(display_name)
