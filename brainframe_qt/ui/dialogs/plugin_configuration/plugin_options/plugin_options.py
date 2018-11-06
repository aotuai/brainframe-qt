from typing import Dict, List

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QGroupBox
from PyQt5.uic import loadUi

from .option_items import (
    PluginOptionItem,
    EnumOptionItem,
    FloatOptionItem,
    IntOptionItem,
    BoolOptionItem
)
from brainframe.shared.codec_enums import OptionType
from brainframe.client.api import api, codecs
from brainframe.client.ui.resources.paths import qt_ui_paths


class PluginOptionsWidget(QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.plugin_options_ui, self)
        self.option_items: List[PluginOptionItem] = []
        self.grid_layout = self.grid.layout()

    @pyqtSlot(str)
    def change_plugin(self, plugin_name):
        """When an item on the QListWidget is selected

        Connected to:
        - PluginList -- QtDesigner
          [peer].plugin_changed
        """
        self._remove_existing_widgets()

        print("Change the plugin: ", plugin_name)
        options = api.get_plugin_options(plugin_name)
        for option_name, option in options.items():
            self.add_option(option_name, option)

    def add_option(self, name: str, option: codecs.PluginOption):
        if option.type is OptionType.BOOL:
            item = BoolOptionItem(name, option, parent=self)
        elif option.type is OptionType.ENUM:
            item = EnumOptionItem(name, option, parent=self)
        elif option.type is OptionType.FLOAT:
            item = FloatOptionItem(name, option, parent=self)
        elif option.type is OptionType.INT:
            item = IntOptionItem(name, option, parent=self)
        else:
            raise TypeError("The plugin option of name " + str(name) +
                            " has an invalid type of type " + str(option.type))
        print(name, option)
        _NAME_ROW = 0
        _VALUE_ROW = 1
        _ENABLE_ROW = 2

        option_row = len(self.option_items) + 2

        self.grid_layout.addWidget(item.label_widget, option_row, _NAME_ROW)
        self.grid_layout.addWidget(item.option_widget, option_row, _VALUE_ROW)

        item.set_val(option.value)
        self.option_items.append(item)

    def _remove_existing_widgets(self):
        for option_item in self.option_items:
            option_item.label_widget.deleteLater()
            option_item.option_widget.deleteLater()
        self.option_items = []
