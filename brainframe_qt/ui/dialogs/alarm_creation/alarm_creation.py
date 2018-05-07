from enum import Enum
from typing import List

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.uic import loadUi

from brainframe.client.api.codecs import (
    Attribute,
    EngineConfiguration,
    Zone,
    ZoneAlarm,
    ZoneAlarmCondition,
    ZoneAlarmRateCondition
)
from brainframe.client.ui.resources.paths import qt_ui_paths


class AlarmCreationDialog(QDialog):
    # noinspection PyArgumentList
    # PyCharm incorrectly complains
    ConditionType = Enum("ConditionType", ["count", "rate"])

    def __init__(self, zones: List[Zone],
                 engine_config: EngineConfiguration,
                 parent=None):
        super().__init__(parent)

        loadUi(qt_ui_paths.alarm_creation_ui, self)

        self.engine_conf = engine_config
        self.zones = zones

        self._update_combo_box(self.test_type_combo_box,
                               ZoneAlarmCondition.test_types)

        detection_classes = self.engine_conf.attribute_ownership
        self._update_combo_box(self.countable_combo_box,
                               detection_classes.keys())

        # Set the behavior combo box to have initial attributes values
        detection_class = self.countable_combo_box.currentText()
        self._update_attribute_values(detection_class)
        # Update the attribute values when the behavior selection changes
        self.countable_combo_box.currentTextChanged.connect(
            self._update_attribute_values)

        self._update_combo_box(self.zone_combo_box,
                               [zone.name for zone in zones])

        # Input sanitation
        self.alarm_name.textEdited.connect(self.verify_inputs_valid)
        self.behavior_combo_box.currentTextChanged.connect(
            self.verify_inputs_valid)
        self.verify_inputs_valid()

        # Condition type
        self.condition_type_button_group.buttonClicked.connect(
            self.condition_type_button_changed)
        self.set_condition_type(self.ConditionType.count)

    def condition_type_button_changed(self):
        checked_button = self.condition_type_button_group.checkedButton()
        if checked_button is self.count_based_button:
            self.set_condition_type(self.ConditionType.count)
        elif checked_button is self.rate_based_button:
            self.set_condition_type(self.ConditionType.rate)

    def set_condition_type(self, condition_type: ConditionType):
        if condition_type == self.ConditionType.count:
            self.hide_count_widgets(False)
            self.hide_rate_widgets(True)
        if condition_type == self.ConditionType.rate:
            self.hide_count_widgets(True)
            self.hide_rate_widgets(False)

    def hide_count_widgets(self, hidden):
        """Hide widgets used when using count conditions"""
        self.behavior_combo_box.setHidden(hidden)
        self.in_count_label.setHidden(hidden)

    def hide_rate_widgets(self, hidden):
        """Hide widgets used when using rate conditions"""
        self.direction_combo_box.setHidden(hidden)
        self.in_rate_label.setHidden(hidden)
        self.duration_spin_box.setHidden(hidden)
        self.seconds_label.setHidden(hidden)

    @classmethod
    def new_alarm(cls, *, zones, engine_config):
        dialog = cls(zones, engine_config, None)
        result = dialog.exec_()

        zones = {zone.name: zone for zone in zones}  # type: List[Zone]

        if not result:
            return None, None

        alarm_name = dialog.alarm_name.text()
        condition_type = dialog.condition_type_button_group.checkedButton()
        test_type = dialog.test_type_combo_box.currentText()
        count = dialog.count_spin_box.value()
        countable = dialog.countable_combo_box.currentText()
        zone = dialog.zone_combo_box.currentText()
        start_time = dialog.start_time_edit.time().toString("HH:mm:ss")
        stop_time = dialog.stop_time_edit.time().toString("HH:mm:ss")

        count_condition = None
        rate_condition = None

        if condition_type == "Count Based":
            behavior = dialog.behavior_combo_box.currentText()

            # Find category that attribute value is a part of
            for category in engine_config.attribute_ownership[countable]:
                if behavior in engine_config.attributes[category]:
                    break
            else:
                category = None

            if behavior == "":
                # No behavior was selected
                attribute = None
            else:
                attribute = Attribute(category=category, value=behavior)

            count_condition = ZoneAlarmCondition(test=test_type,
                                                 check_value=count,
                                                 with_class_name=countable,
                                                 attribute=attribute)

        elif condition_type == "Rate Based":
            direction = dialog.direction_combo_box.currentText()
            duration = dialog.duration_spin_box.value()

            if direction == "enter":
                direction = ZoneAlarmRateCondition.DirectionType.entering
            elif direction == "exit":
                direction = ZoneAlarmRateCondition.DirectionType.exiting
            elif direction == "enter/exit":
                direction = \
                    ZoneAlarmRateCondition.DirectionType.entering_or_exiting

            rate_condition = ZoneAlarmRateCondition(test=test_type,
                                                     change=count,
                                                     direction=direction,
                                                     duration=duration,
                                                     with_class_name=countable,
                                                     attribute=None)

        else:
            raise ValueError(f"Invalid condition type '{condition_type}'")

        alarm = ZoneAlarm(name=alarm_name,
                          count_conditions=[count_condition],
                          rate_conditions=[rate_condition],
                          active_start_time=start_time,
                          active_end_time=stop_time,
                          use_active_time=True)  # TODO: False?

        zones[zone].alarms.append(alarm)

        return zones[zone], alarm

    @pyqtSlot()
    def verify_inputs_valid(self):
        """Return True or false if the inputs are valid"""
        is_valid = True
        if self.alarm_name.text().strip() == "":
            is_valid = False

        self.dialog_button_box.button(QDialogButtonBox.Ok).setEnabled(is_valid)

    @pyqtSlot(str)
    def countable_index_changed(self, countable):
        self._update_combo_box(self.behavior_combo_box,
                               self.engine_conf.attributes[countable])

    @classmethod
    def _update_combo_box(cls, combo_box, items):
        combo_box.clear()
        combo_box.insertItems(0, items)

    def _update_attribute_values(self, detection_class):
        detection_classes = self.engine_conf.attribute_ownership
        attributes = self.engine_conf.attributes

        if detection_class:
            # Get all attribute values a detection_class can have
            attribute_values = [attributes[category] for category in
                                detection_classes[detection_class]]

            # Sum all lists and add also add empty entry
            attribute_values = sum(attribute_values, [''])
            self._update_combo_box(self.behavior_combo_box,
                                   attribute_values)
