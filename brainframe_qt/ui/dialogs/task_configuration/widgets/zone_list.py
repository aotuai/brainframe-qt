from typing import Dict, Callable, List

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from brainframe.api import bf_codecs

from ..core.zone import Zone
from .zone_list_item import ZoneListAlarmItem, ZoneListZoneItem


class ZoneList(QWidget):
    initiate_zone_edit = pyqtSignal(int)
    zone_delete = pyqtSignal(int)
    alarm_delete = pyqtSignal(int)

    zone_name_change = pyqtSignal(int, str)

    layout: Callable[..., QVBoxLayout]

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.stream_id = None

        # Lookup table to get zone/alarm from id (used during deletion)
        self.zones: Dict[int, ZoneListZoneItem] = {}
        self.alarms: Dict[int, ZoneListAlarmItem] = {}

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QVBoxLayout()

        self.setLayout(layout)

    def _init_style(self) -> None:
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)

    def add_zone(self, zone: Zone) -> ZoneListZoneItem:
        """Creates and returns the new ZoneListItem using the Zone"""
        zone_item = ZoneListZoneItem(zone, parent=self)

        self.zones[zone.id] = zone_item

        zone_item.zone_edit.connect(self.initiate_zone_edit)
        zone_item.zone_delete.connect(self.zone_delete)
        zone_item.zone_name_change.connect(self.zone_name_change)

        self.layout().addWidget(zone_item)

        for alarm in zone.alarms:
            self.add_alarm(zone, alarm)

        return zone_item

    def confirm_zone(self, zone: Zone) -> None:
        assert None in self.zones

        self.remove_zone(None)
        self.add_zone(zone)

    def update_zone(self, zone: Zone) -> None:
        old_zone_widget = self.zones[zone.id]
        new_zone_widget = self.add_zone(zone)

        self.layout().replaceWidget(old_zone_widget, new_zone_widget)

        old_zone_widget.deleteLater()

    def add_alarm(self, zone: Zone, alarm: bf_codecs.ZoneAlarm):
        alarm_widget = ZoneListAlarmItem(alarm, parent=self)

        self.alarms[alarm.id] = alarm_widget

        alarm_widget.alarm_delete.connect(self.alarm_delete)

        self._add_alarm_widget(alarm_widget, zone.id)

    def remove_alarm(self, alarm_id: int) -> None:
        alarm_widget = self.alarms.pop(alarm_id)

        self.layout().removeWidget(alarm_widget)

        alarm_widget.deleteLater()

    def remove_zone(self, zone_id: int) -> None:
        zone_widget: ZoneListZoneItem = self.zones.pop(zone_id)

        alarm_widgets = self._find_alarm_widgets_for_zone(zone_widget)

        # Remove zone and all child alarms
        self.layout().removeWidget(zone_widget)
        for alarm_widget in alarm_widgets:
            # Uses private attribute for now, but this is temporary until zone widgets
            # contain alarm widgets inside of them
            self.remove_alarm(alarm_widget._alarm.id)

        zone_widget.deleteLater()

    def _add_alarm_widget(self, alarm_widget: ZoneListAlarmItem, zone_id: int) -> None:
        """Add an alarm widget to the correct zone"""
        zone_widget = self.zones[zone_id]
        zone_index = self.layout().indexOf(zone_widget)

        index = 0
        for index in range(zone_index, self.layout().count()):
            widget_item = self.layout().itemAt(index)
            widget = widget_item.widget()
            if isinstance(widget, ZoneListZoneItem):
                break

        insert_index = index + 1

        self.layout().insertWidget(insert_index, alarm_widget)

    def _find_alarm_widgets_for_zone(
        self, zone_widget: ZoneListZoneItem
    ) -> List[ZoneListAlarmItem]:
        """Find all child alarm widgets for a zone widget"""

        zone_index = self.layout().indexOf(zone_widget)

        # Find all child alarms
        alarm_widgets: List[ZoneListAlarmItem] = []
        for index in range(zone_index + 1, self.layout().count()):
            widget_item = self.layout().itemAt(index)
            widget = widget_item.widget()

            if isinstance(widget, ZoneListZoneItem):
                break

            if isinstance(widget, ZoneListAlarmItem):
                alarm_widgets.append(widget)

        return alarm_widgets
