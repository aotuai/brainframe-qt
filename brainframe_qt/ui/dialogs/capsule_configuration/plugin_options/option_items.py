from abc import ABC, abstractmethod
import logging
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QCursor
from PyQt5.QtWidgets import QWidget, QComboBox, QCheckBox, QLabel, QLineEdit, \
    QPushButton, QSizePolicy, QApplication, QMessageBox

from brainframe.client.ui.dialogs.capsule_configuration import plugin_utils
from brainframe.client.ui.resources.ui_elements.buttons import TextIconButton


class PluginOptionItem(ABC):
    # To be filled in by subclass
    option_widget: QWidget = None
    change_signal = None

    def __init__(self, name: str, initial_value,
                 description: Optional[str] = None,
                 parent=None):

        self.option_name = name
        self.description = description
        self.parent = parent

        self.label_widget: QLabel = None
        self.override_checkbox: QCheckBox = None
        self.tooltip_button: QPushButton = None

        self.pretty_name = plugin_utils.pretty_snakecase(self.option_name)
        self.init_ui(self.pretty_name, description, parent)

        self.locked = None
        """When 'locked' is True or False, a checkbox will appear for allowing
        the option to become locked or unlocked by the user. This is intended
        for allowing global options to be explicitly overridden for a stream."""

        self.initial_value = initial_value
        self.set_val(self.initial_value)

        # By default, we don't show the override checkbox.
        self.set_locked(False)
        self.show_lock(False)

    def init_ui(self, pretty_name, description, parent):
        self.label_widget = QLabel(pretty_name, parent=parent)
        self.override_checkbox = QCheckBox(parent=parent)

        self.label_widget.setSizePolicy(QSizePolicy.Expanding,
                                        QSizePolicy.Preferred)

        # Set tooltip of description button and disable button, otherwise no
        # button
        if description:
            self.tooltip_button = TextIconButton("❓", parent=parent)
            self.tooltip_button.setFlat(True)
            self.tooltip_button.setToolTip(description)
            # self.tooltip_button.setDisabled(True)
            self.tooltip_button.setToolTipDuration(0)
            self.tooltip_button.setCursor(QCursor(Qt.WhatsThisCursor))

            # Make it so if you click an option, the description appears
            msg = QMessageBox(parent=self.tooltip_button)
            msg.setText(description)
            msg.setWindowTitle(f"About: {self.pretty_name}")
            self.tooltip_button.clicked.connect(lambda: msg.exec())
        else:
            self.tooltip_button = None

        # Connect the lock signals
        self.override_checkbox.clicked.connect(
            lambda checked: self.set_locked(not checked))

    @abstractmethod
    def set_val(self, value):
        pass

    @property
    @abstractmethod
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
        self.override_checkbox.setVisible(status)

    def set_locked(self, locked: bool):
        """
        Connected to:
        - QCheckBox -- dynamic
          self.lock_checkbox.clicked.connect
        """
        self.locked = locked
        self.option_widget.setEnabled(not locked)
        self.override_checkbox.setChecked(not locked)

    def delete(self):
        self.label_widget.deleteLater()
        self.option_widget.deleteLater()
        self.override_checkbox.deleteLater()
        if self.tooltip_button:
            self.tooltip_button.deleteLater()


class EnumOptionItem(PluginOptionItem):
    """A plugin option that holds a choice from a discrete set of string values.
    """

    def __init__(self, name: str, value: str, constraints,
                 description: Optional[str] = None,
                 parent=None):
        self.option_widget = QComboBox(parent=parent)
        self.change_signal = self.option_widget.currentIndexChanged

        # Get constraints
        self._choices = constraints["choices"]

        for choice_text in self._choices:
            pretty_choice = plugin_utils.pretty_snakecase(choice_text)
            self.option_widget.addItem(pretty_choice)

        super().__init__(name, value, description, parent=parent)

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

    def __init__(self, name: str, value: float, constraints,
                 description: Optional[str] = None,
                 parent=None):
        self.option_widget = QLineEdit(parent=parent)
        self.change_signal = self.option_widget.textChanged

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
        super().__init__(name, value, description, parent=parent)

    def set_val(self, value: float):
        self.option_widget.setText(str(value))

    @property
    def val(self):
        try:
            num = float(self.option_widget.text())
            return num
        except ValueError:
            logging.warning(QApplication.translate("FloatOptionItem",
                                                   "{} is not a float!")
                            .format(self.option_widget.text()))
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

    def __init__(self, name: str, value: int, constraints,
                 description: Optional[str] = None,
                 parent=None):
        super().__init__(name, value, constraints, description, parent=parent)

    @property
    def val(self):
        return int(super().val)


class BoolOptionItem(PluginOptionItem):
    """A plugin option that holds an boolean value."""

    def __init__(self, name: str, value: bool, _,
                 description: Optional[str] = None,
                 parent=None):
        self.option_widget = QCheckBox(parent=parent)
        self.change_signal = self.option_widget.stateChanged

        super().__init__(name, value, description, parent=parent)

    def set_val(self, value: bool):
        self.option_widget.setChecked(value)

    @property
    def val(self):
        return self.option_widget.isChecked()

    def is_valid(self):
        return isinstance(self.val, bool)
