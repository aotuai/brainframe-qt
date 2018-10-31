from typing import Dict

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.uic import loadUi

from .plugin_list_item.plugin_list_item import PluginListItem
from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths


class PluginList(QListWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.plugin_list_ui, self)
        print("Ahhh, the PluginList UI has been loaded indeed")
        # Things that exist
        # print(self.plugin_container)

        # Query API for existing plugins

        # Populate plugin_container layout with those plugins
        plugin_names = api.get_plugin_names()

        for plugin_name in plugin_names:
            list_widget_item = QListWidgetItem(parent=self)
            self.addItem(list_widget_item)

            item_widget = PluginListItem(name=plugin_name, parent=self)

            # Fix sizing
            list_widget_item.setSizeHint(item_widget.sizeHint())
            self.setItemWidget(list_widget_item, item_widget)

        # Always have an item selected
        if len(plugin_names):
            self.setCurrentRow(0)

    @pyqtSlot(QListWidgetItem)
    def item_selected(self, current_item):
        """When an item on the QListWidget is selected

        Connected to:
        - PluginList -- QtDesigner
          self.currentItemChanged
        """
        print("Clicked!")
        plugin_list_item = self.itemWidget(current_item)

        print("Ahh, an item has been selected indeed",
              plugin_list_item.plugin_name)
