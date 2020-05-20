from typing import Dict, List, Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QGroupBox, QApplication
from PyQt5.uic import loadUi

from .option_items import (
    PluginOptionItem,
    EnumOptionItem,
    FloatOptionItem,
    IntOptionItem,
    BoolOptionItem
)
from brainframe.shared.codec_enums import OptionType
from brainframe.client.api import api
from brainframe.client.ui.dialogs.capsule_configuration import plugin_utils
from brainframe.client.ui.resources.paths import qt_ui_paths


class BasePluginOptionsWidget(QGroupBox):
    plugin_options_changed = pyqtSignal()
    """Alerts the dialog holding the options widget that the current options
    have been modified by the user, such options may or may not be valid
    
    Connected to:
    - CapsuleConfigDialog -- Dynamic
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

        self.grid_layout: QGridLayout = self.grid.layout()

        self.current_plugin = None

    def change_plugin(self, plugin_name):
        """When an item on the QListWidget is selected
        :param plugin_name: The name of the plugin to edit options for
        """
        self._reset()
        self.current_plugin = plugin_name
        plugin = api.get_plugin(plugin_name)

        # Change name of plugin
        title = f"[{plugin_utils.pretty_snakecase(plugin_name)}] "
        title += self.tr("Options")
        self.setTitle(title)

        # Set plugin description
        plugin_description = plugin.description or ""
        self.plugin_description_area.setVisible(bool(plugin_description))
        self.plugin_description_label.setText(plugin_description)

        # Add configuration that every plugin _always_ has
        self.enabled_option = self._add_option(
            name=self.tr("Plugin Enabled"),
            type_=OptionType.BOOL,
            value=api.is_plugin_active(plugin_name, stream_id=None),
            constraints={})
        self.all_items.append(self.enabled_option)

        # Add options specific to this plugin
        option_values = api.get_plugin_option_vals(plugin_name)
        for option_name, option in plugin.options.items():
            item = self._add_option(
                name=option_name,
                type_=option.type,
                value=option_values[option_name],
                constraints=option.constraints,
                description=option.description)

            # Keep track of the option
            self.option_items.append(item)
            self.all_items.append(item)

    def options_valid(self):
        """Returns True if none of the options are invalid.

        Essentially, it checks the validator for each option and verifies that
        they are all within the correct types and ranges.
        """
        return all(option.is_valid() for option in self.all_items)

    def _add_option(self, name: str, type_: OptionType, value,
                    constraints: Dict, description: Optional[str] = None):

        parent = self
        args = name, value, constraints, description, parent

        if type_ is OptionType.BOOL:
            item = BoolOptionItem(*args)
        elif type_ is OptionType.ENUM:
            item = EnumOptionItem(*args)
        elif type_ is OptionType.FLOAT:
            item = FloatOptionItem(*args)
        elif type_ is OptionType.INT:
            item = IntOptionItem(*args)
        else:
            message = QApplication.translate(
                "BasePluginOptionsWidget",
                "The plugin option of name {} has an invalid type of type {}")
            message = message.format(name, type_)
            raise TypeError(message)

        _TOOLTIP_COL = 0
        _NAME_COL = 1
        _VALUE_COL = 2
        _SPACER_COL = 3
        _ENABLE_COL = 4

        row = len(self.all_items) + 2

        self.grid_layout.addWidget(item.label_widget, row, _NAME_COL)
        if item.tooltip_button:
            self.grid_layout.addWidget(item.tooltip_button, row, _TOOLTIP_COL)
        self.grid_layout.addWidget(item.option_widget, row, _VALUE_COL)
        self.grid_layout.addWidget(item.override_checkbox, row, _ENABLE_COL,
                                   Qt.AlignRight)

        # Whenever this option is changed, make sure that our signal emits
        item.change_signal.connect(self._on_inputs_changed)

        return item

    def apply_changes(self, stream_id=None):
        """This will send changes to the server for this plugin
        Connected to:
        - QButtonBox -- Dynamic
          [child].button(QDialogButtonBox.Apply).clicked
        """
        # Make sure that the options are valid
        if not self.options_valid():
            message = QApplication.translate(
                "BasePluginOptionsWidget",
                "Not all options are valid!")
            raise ValueError(message)
        if not len(self.all_items):
            message = QApplication.translate(
                "BasePluginOptionsWidget",
                "You can't apply changes if the plugin never got set!")
            raise RuntimeError(message)

        unlocked_option_vals = {option_item.option_name: option_item.val
                                for option_item in self.option_items
                                if not option_item.locked}

        api.set_plugin_option_vals(
            plugin_name=self.current_plugin,
            stream_id=stream_id,
            option_vals=unlocked_option_vals)

        if not self.enabled_option.locked:
            api.set_plugin_active(
                plugin_name=self.current_plugin,
                stream_id=stream_id,
                active=self.enabled_option.val)
        else:
            api.set_plugin_active(
                plugin_name=self.current_plugin,
                stream_id=stream_id,
                active=None)

    def _on_inputs_changed(self):
        """
        This gets called when any plugin option gets edited/changed
        The 'on_change' from the child could be a variety of signals,
        depending on the specific subclass of the PluginOption Item.

        Connected to:
        - PluginOptionItem -- Dynamic
         [child].change_signal
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
