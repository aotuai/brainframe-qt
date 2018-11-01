from typing import Dict

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QGroupBox
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths


class PluginOption:
    pass


class PluginOptionsWidget(QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.plugin_options_ui, self)
        self.options = []

    @pyqtSlot(str)
    def change_plugin(self, plugin_name):
        """When an item on the QListWidget is selected

        Connected to:
        - PluginList -- QtDesigner
          [peer].item_selected
        """
        print("Change the plugin: ", plugin_name)
        options = api.get_plugin_options(plugin_name)
        for option_name, option in options.items():
            print(option_name, option)

    def add_option(self):
        pass
