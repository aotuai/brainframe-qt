import logging
from abc import ABC, abstractmethod, abstractproperty
from typing import List, Callable

from PyQt5.QtWidgets import (
    QLabel,
    QWidget,
    QComboBox,
    QCheckBox,
    QLineEdit
)
from PyQt5.QtGui import QIntValidator, QDoubleValidator

from brainframe.client.ui.dialogs.plugin_configuration import plugin_utils


class PluginOptionItem(ABC):
    option_widget: QWidget = None
    """To be filled in by subclass"""

    def __init__(self, name: str, initial_value, parent=None):
        self.option_name = name
        self.locked = None
        """When 'locked' is True or False, a checkbox will appear for allowing
        the option to become locked or unlocked by the user. This is intended
        for allowing global options to be explicitly overridden for a stream."""

        pretty_name = plugin_utils.pretty_snakecase(self.option_name)

        self.label_widget = QLabel(pretty_name, parent=parent)
        self.lock_checkbox = QCheckBox(parent=parent)
        self.initial_value = initial_value

        self.set_val(self.initial_value)

        # Connect the lock signals
        self.lock_checkbox.clicked.connect(lambda e: self.set_locked(not e))
        self.locked = False

        # By default, we don't show the override checkbox.
        self.set_locked(False)
        self.show_lock(False)

    @abstractmethod
    def set_val(self, value):
        pass

    @abstractproperty
    def val(self):
        """This should return the current value for the widget"""
        pass

    @abstractmethod
    def is_valid(self):
        """Should return True or False if the current value of the option is
        valid, or if it does not fit the rules set by the plugin."""
        raise NotImplementedError

    def show_lock(self, status: bool):
        """By default the override lock is hidden."""
        self.lock_checkbox.setVisible(status)

    def set_locked(self, status: bool):
        """
        Connected to:
        - QCheckBox -- dynamic
          self.lock_checkbox.clicked.connect
        """
        self.locked = status
        self.option_widget.setEnabled(not status)
        self.lock_checkbox.setChecked(not status)

    def delete(self):
        self.label_widget.deleteLater()
        self.option_widget.deleteLater()
        self.lock_checkbox.deleteLater()


class EnumOptionItem(PluginOptionItem):
    """A plugin option that holds a choice from a discrete set of string values.
    """

    def __init__(self, name: str, value: str, constraints, parent=None):
        self.option_widget = QComboBox(parent=parent)
        self.on_change = self.option_widget.currentIndexChanged.connect

        # Get constraints
        self._choices = constraints["choices"]

        for choice_text in self._choices:
            pretty_choice = plugin_utils.pretty_snakecase(choice_text)
            self.option_widget.addItem(pretty_choice)

        super().__init__(name, value, parent=parent)

    def set_val(self, value: str):
        index = self._choices.index(value)
        self.option_widget.setCurrentIndex(index)

    @property
    def val(self):
        return self._choices[self.option_widget.currentIndex()]

    def is_valid(self):
        return self.val in self._choices


class FloatOptionItem(PluginOptionItem):
    """A plugin option that holds a floating point value with defined
    boundaries.

    Can have min_val or max_val be None"""
    _validator_type = QDoubleValidator

    def __init__(self, name: str, value: float, constraints, parent=None):
        self.option_widget = QLineEdit(parent=parent)
        self.on_change = self.option_widget.textChanged.connect

        # Get constraints
        self._min_val = constraints["min_val"]
        self._max_val = constraints["max_val"]

        validator = self._validator_type()
        if self._min_val is not None:
            validator.setBottom(self._min_val)
        if self._max_val is not None:
            validator.setTop(self._max_val)

        if isinstance(validator, QDoubleValidator):
            validator.setNotation(QDoubleValidator.StandardNotation)

        self.option_widget.setValidator(validator)
        super().__init__(name, value, parent=parent)

    def set_val(self, value: float):
        self.option_widget.setText(str(value))

    @property
    def val(self):
        try:
            num = float(self.option_widget.text())
            return num
        except ValueError:
            logging.warning(str(self.option_widget.text()) + " is not a float!")
            return None

    def is_valid(self):
        # The self._validator_type should take care of validation of types
        text = self.option_widget.text()
        status, _, _ = self.option_widget.validator().validate(text, 0)
        return status == self._validator_type.Acceptable


class IntOptionItem(FloatOptionItem):
    """A plugin option that holds an integer value.

    Can have min_val and max_val be None
    """
    _validator_type = QIntValidator

    def __init__(self, name: str, value: int, constraints, parent=None):
        super().__init__(name, value, constraints, parent=parent)

    @property
    def val(self):
        return int(super().val)


class BoolOptionItem(PluginOptionItem):
    """A plugin option that holds an boolean value."""

    def __init__(self, name: str, value: bool, constraints, parent=None):
        self.option_widget = QCheckBox(parent=parent)
        self.on_change = self.option_widget.stateChanged.connect

        super().__init__(name, value, parent=parent)

    def set_val(self, value: bool):
        self.option_widget.setChecked(value)

    @property
    def val(self):
        return self.option_widget.isChecked()

    def is_valid(self):
        return isinstance(self.val, bool)
