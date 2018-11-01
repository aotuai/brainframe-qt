from typing import Dict

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.uic import loadUi

from .plugin_list_item.plugin_list_item import PluginListItem
from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths


class PluginList(QListWidget):
    plugin_selection_changed = pyqtSignal(str)
    """This is activated when the user changes the selected plugin in the
    list.

    Connected to:
    - PluginOptionsWidget -- QtDesigner
      [peer].ongoing_alerts_slot
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.plugin_list_ui, self)

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

    def currentItemChanged(self, current: QListWidgetItem, previous: QListWidgetItem):
        """When an item on the QListWidget is selected

        Connected to:
        - PluginList -- Dynamic
          self.currentItemChanged
        """
        print("hmm item selected")
        plugin_list_item = self.itemWidget(current)
        self.plugin_selection_changed.emit(plugin_list_item.plugin_name)
        print("Yes, it has changed")
    #
    # @pyqtSlot(QListWidgetItem)


