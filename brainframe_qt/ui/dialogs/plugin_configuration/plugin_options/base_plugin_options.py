from typing import Dict, List

from PyQt5.QtCore import pyqtSlot, pyqtSignal
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


class BasePluginOptionsWidget(QGroupBox):
    plugin_options_changed = pyqtSignal()
    """Alerts the dialog holding the options widget that the current options
    have been modified by the user, such options may or may not be valid
    
    Connected to:
    - PluginConfigDialog -- Dynamic
      [parent].is_inputs_valid
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.plugin_options_ui, self)

        self.option_items: List[PluginOptionItem] = []
        """Only plugin-specific option items. This does not include items that 
        exist for all plugins, such as 'plugin_enabled'."""

        self.all_items: List[PluginOptionItem] = []
        """All option items, including special cases such as 
        self.enabled_option"""

        self.enabled_option: BoolOptionItem = None
        """This holds the option for enabling and disabling a plugin."""

        self.grid_layout = self.grid.layout()

        self.current_plugin = None

    def change_plugin(self, plugin_name, stream_id=None):
        """When an item on the QListWidget is selected

        :param stream_id: If None, then this options widget is global.
        If not None, this will be options for a specific stream.
        :param plugin_name: The name of the plugin to edit options for
        """
        self._reset()
        self.current_plugin = plugin_name

        # Add configuration that every plugin _always_ has
        self.enabled_option = self.add_option(
            name="Plugin Enabled",
            type=OptionType.BOOL,
            value=api.is_plugin_active(plugin_name, stream_id=None),
            constraints={})
        self.all_items.append(self.enabled_option)

        # Add options specific to this plugin
        options = api.get_plugin_options(plugin_name)
        print("Thine said options", options)
        for option_name, option in options.items():
            item = self.add_option(
                name=option_name,
                type=option.type,
                value=option.value,
                constraints=option.constraints)
            # Keep track of the option
            self.option_items.append(item)
            self.all_items.append(item)

    def options_valid(self):
        """Returns True if none of the options are invalid.

        Essentially, it checks the validator for each option and verifies that
        they are all within the correct types and ranges.
        """
        for option in self.all_items:
            if not option.is_valid():
                return False
        return True

    def add_option(self, name: str, type: OptionType, value, constraints: Dict):
        if type is OptionType.BOOL:
            item = BoolOptionItem(name, value, constraints, parent=self)
        elif type is OptionType.ENUM:
            item = EnumOptionItem(name, value, constraints, parent=self)
        elif type is OptionType.FLOAT:
            item = FloatOptionItem(name, value, constraints, parent=self)
        elif type is OptionType.INT:
            item = IntOptionItem(name, value, constraints, parent=self)
        else:
            raise TypeError("The plugin option of name " + str(name) +
                            " has an invalid type of type " + str(type))

        _NAME_ROW = 0
        _VALUE_ROW = 1
        _ENABLE_ROW = 2

        option_row = len(self.all_items) + 2

        self.grid_layout.addWidget(item.label_widget, option_row, _NAME_ROW)
        self.grid_layout.addWidget(item.option_widget, option_row, _VALUE_ROW)

        # Whenever this option is changed, make sure that our signal emits
        item.on_change(self._on_inputs_changed)

        return item

    def apply_changes(self):
        """This will send changes to the server for this plugin
        Connected to:
        - QButtonBox -- Dynamic
          [child].button(QDialogButtonBox.Apply).clicked
        """
        # Make sure that the options are valid
        if not self.options_valid():
            raise ValueError("Not all options are valid!")
        if not len(self.all_items):
            raise RuntimeError("You can't apply changes if the plugin never"
                               " got set!")

        option_vals = {option_item.option_name: option_item.val
                       for option_item in self.option_items}

        api.set_plugin_option_vals(plugin_name=self.current_plugin,
                                   stream_id=None,
                                   option_vals=option_vals)

    def _on_inputs_changed(self):
        """
        This gets called when any plugin option gets edited/changed
        The 'on_change' from the child could be a variety of signals,
        depending on the specific subclass of the PluginOption Item.

        Connected to:
        - PluginOptionItem -- Dynamic
         [child].on_change
        """
        self.plugin_options_changed.emit()

    def _reset(self):
        """Clear any state specific to any one plugin"""

        # Tell QT to delete widgets
        for option_item in self.all_items:
            option_item.delete()

        # Clear references
        self.enabled_option = None
        self.current_plugin = None
        self.option_items = []
        self.all_items = []
