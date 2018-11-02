from abc import ABC

from PyQt5.QtWidgets import QLabel

from brainframe.client.api.codecs import PluginOption
from brainframe.client.ui.dialogs.plugin_configuration import plugin_utils


class PluginOptionItem(ABC):
    def __init__(self, name: str, option: PluginOption):
        self.option_name = name
        self.option = option
        
        pretty_name = plugin_utils.pretty_plugin_name(self.option_name)
        self.label_widget = QLabel(pretty_name)


class EnumOptionItem(PluginOptionItem):
    """A plugin option that holds a choice from a discrete set of string values.
    """

    def __init__(self, name, option: PluginOption):
        super().__init__(name, option)


class FloatOptionItem(PluginOptionItem):
    """A plugin option that holds a floating point value with defined
    boundaries.

    Can have min_val or max_val be None"""

    def __init__(self, name, option: PluginOption):
        super().__init__(name, option)


class IntOptionItem(PluginOptionItem):
    """A plugin option that holds an integer value.

    Can have min_val and max_val be None
    """

    def __init__(self, name, option: PluginOption):
        super().__init__(name, option)


class BoolOptionItem(PluginOptionItem):
    """A plugin option that holds an boolean value."""

    def __init__(self, name, option: PluginOption):
        super().__init__(name, option)
