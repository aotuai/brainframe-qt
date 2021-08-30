from typing import Dict, Callable, List

from PyQt5.QtCore import QModelIndex, pyqtSlot, pyqtSignal, Qt
from PyQt5.QtWidgets import QStyleOptionViewItem, QStyledItemDelegate, QWidget, \
    QVBoxLayout

from brainframe.api import bf_codecs

from brainframe_qt.api_utils import api

from ..core.zone import Zone
from .zone_list_item import ZoneListAlarmItem, ZoneListZoneItem


class ZoneList(QWidget):
    initiate_zone_edit = pyqtSignal(int)
    zone_delete = pyqtSignal(int)

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

        # self.layout().setSpacing(1)

        # # Item delegate is used to force a custom row height
        # self.setItemDelegate(ZoneListItemDelegate(row_height=40))
        #
        # # Scale columns in view
        # self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # self.header().setSectionResizeMode(1, QHeaderView.Stretch)
        # self.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        # self.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)

    def add_zone(self, zone: Zone) -> ZoneListZoneItem:
        """Creates and returns the new ZoneListItem using the Zone"""
        zone_item = ZoneListZoneItem(zone, parent=self)

        self.zones[zone.id] = zone_item

        zone_item.zone_edit.connect(self.initiate_zone_edit)
        zone_item.zone_delete.connect(self.zone_delete)

        self.layout().addWidget(zone_item)

        for alarm in zone.alarms:
            self.add_alarm(zone, alarm)

        return zone_item

    def confirm_zone(self, zone: Zone) -> None:
        assert None in self.zones

        self.remove_zone(None)
        self.add_zone(zone)

    def add_alarm(self, zone: Zone, alarm: bf_codecs.ZoneAlarm):
        alarm_item = ZoneListAlarmItem(alarm, parent=self)

        self.alarms[alarm.id] = alarm_item

        zone_item = self.zones[zone.id]
        zone_index = self.layout().indexOf(zone_item)

        index = 0
        for index in range(zone_index, self.layout().count()):
            widget_item = self.layout().itemAt(index)
            widget = widget_item.widget()
            if isinstance(widget, ZoneListZoneItem):
                break

        insert_index = index + 1

        self.layout().insertWidget(insert_index, alarm_item)

    @pyqtSlot(int, int)
    def delete_alarm(self, zone_id: int, alarm_id: int):

        zone_item = self.zones[zone_id]
        alarm_item = self.alarms[alarm_id]

        # Delete alarm from database
        api.delete_zone_alarm(alarm_id)

        # Delete the alarm ZoneListItem from tree
        zone_item.removeChild(alarm_item)

    def remove_zone(self, zone_id: int) -> None:
        zone_widget: ZoneListZoneItem = self.zones.pop(zone_id)
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

        # Remove zone and all child alarms
        self.layout().removeWidget(zone_widget)
        for alarm_widget in alarm_widgets:
            self.layout().removeWidget(alarm_widget)
