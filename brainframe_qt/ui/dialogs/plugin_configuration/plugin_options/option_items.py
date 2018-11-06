from abc import ABC, abstractmethod

from PyQt5.QtWidgets import (
    QLabel,
    QWidget,
    QComboBox,
    QCheckBox,
    QLineEdit
)
from PyQt5.QtGui import QIntValidator, QDoubleValidator

from brainframe.client.api.codecs import PluginOption
from brainframe.client.ui.dialogs.plugin_configuration import plugin_utils


class PluginOptionItem(ABC):
    def __init__(self, name: str, option: PluginOption, parent=None):
        self.option_name = name
        self.option = option

        pretty_name = plugin_utils.pretty_snakecase(self.option_name)

        self.label_widget = QLabel(pretty_name, parent=parent)
        self.option_widget: QWidget = None

    @abstractmethod
    def set_val(self, value):
        raise NotImplementedError


class EnumOptionItem(PluginOptionItem):
    """A plugin option that holds a choice from a discrete set of string values.
    """

    def __init__(self, name, option: PluginOption, parent=None):
        super().__init__(name, option)
        self.option_widget = QComboBox(parent=parent)

        for choice_text in option.constraints["choices"]:
            pretty_choice = plugin_utils.pretty_snakecase(choice_text)
            self.option_widget.addItem(pretty_choice)

    def set_val(self, value):
        index = self.option.constraints["choices"].index(value)
        self.option_widget.setCurrentIndex(index)


class FloatOptionItem(PluginOptionItem):
    """A plugin option that holds a floating point value with defined
    boundaries.

    Can have min_val or max_val be None"""

    def __init__(self, name, option: PluginOption, parent=None):
        super().__init__(name, option)
        self.option_widget = QLineEdit(parent=parent)
        self.option_widget.setValidator(QDoubleValidator())

    def set_val(self, value):
        print("Changing to", value)
        self.option_widget.setText(str(value))


class IntOptionItem(PluginOptionItem):
    """A plugin option that holds an integer value.

    Can have min_val and max_val be None
    """

    def __init__(self, name, option: PluginOption, parent):
        super().__init__(name, option)
        self.option_widget = QCheckBox(parent=parent)
        self.option_widget = QLineEdit(parent=parent)
        self.option_widget.setValidator(QIntValidator())

    def set_val(self, value):
        self.option_widget.setText(str(value))


class BoolOptionItem(PluginOptionItem):
    """A plugin option that holds an boolean value."""

    def __init__(self, name, option: PluginOption, parent=None):
        super().__init__(name, option)
        self.option_widget = QCheckBox(parent=parent)

    def set_val(self, value):
        self.option_widget.setChecked(value)
