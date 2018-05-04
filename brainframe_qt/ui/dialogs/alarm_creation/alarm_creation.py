from typing import List

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.uic import loadUi

from brainframe.client.api.codecs import (
    Attribute,
    EngineConfiguration,
    Zone,
    ZoneAlarm,
    ZoneAlarmCondition
)
from brainframe.client.ui.resources.paths import qt_ui_paths


class AlarmCreationDialog(QDialog):

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

    @classmethod
    def new_alarm(cls, *, zones, engine_config):
        dialog = cls(zones, engine_config, None)
        result = dialog.exec_()

        zones = {zone.name: zone for zone in zones}  # type: List[Zone]

        if not result:
            return None, None

        alarm_name = dialog.alarm_name.text()
        test_type = dialog.test_type_combo_box.currentText()
        count = dialog.count_spin_box.value()
        countable = dialog.countable_combo_box.currentText()
        behavior = dialog.behavior_combo_box.currentText()
        zone = dialog.zone_combo_box.currentText()
        start_time = dialog.start_time_edit.time().toString("HH:mm:ss")
        stop_time = dialog.stop_time_edit.time().toString("HH:mm:ss")

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

        alarm_condition = ZoneAlarmCondition(test=test_type,
                                             check_value=count,
                                             with_class_name=countable,
                                             attribute=attribute)
        alarm = ZoneAlarm(name=alarm_name,
                          conditions=[alarm_condition],
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
