from enum import Enum
from typing import Dict

from PyQt5.QtCore import QModelIndex, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QHeaderView, QPushButton, QStyleOptionViewItem,
                             QStyledItemDelegate, QTreeWidget)
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.api.codecs import Zone, ZoneAlarm
# noinspection PyUnresolvedReferences
from brainframe.client.ui.resources import QTAsyncWorker, qt_resources
from brainframe.client.ui.resources.paths import qt_ui_paths
from brainframe.shared.constants import DEFAULT_ZONE_NAME
from .zone_list_item import ZoneListItem


class ZoneList(QTreeWidget):
    EntryType = Enum('EntryType', "REGION LINE ALARM UNKNOWN")

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.zone_list_ui, self)

        # Crashes when set in UI file for some reason
        self.setColumnCount(3)

        # Scale columns in view
        self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        # Item delegate is used to force a custom row height
        self.setItemDelegate(ZoneListItemDelegate(row_height=40))

        self.stream_id = None

        # Lookup table to get zone/alarm from id (used during deletion)
        self.zones: Dict[int, ZoneListItem] = {}
        self.alarms: Dict[int, ZoneListItem] = {}

    def init_zones(self, stream_id):
        """Initialize zone list with zones already in database"""
        self.stream_id = stream_id

        def get_zones():
            return api.get_zones(stream_id)

        def add_zones(zones):
            for zone in zones:
                self.add_zone(zone)

            self.clearSelection()

        QTAsyncWorker(self, get_zones, on_success=add_zones).start()

    def add_zone(self, zone: Zone):
        """Creates and returns the new ZoneListItem using the zone"""

        if zone.name == DEFAULT_ZONE_NAME or len(zone.coords) > 2:
            entry_type = self.EntryType.REGION
        elif len(zone.coords) == 2:
            entry_type = self.EntryType.LINE
        else:
            entry_type = self.EntryType.UNKNOWN

        zone_item = self._new_row(zone.name, entry_type)
        self.addTopLevelItem(zone_item)

        self._add_trash_button(zone_item)
        if zone.name == DEFAULT_ZONE_NAME:
            zone_item.trash_button.setDisabled(True)
        else:
            zone_item.trash_button.clicked.connect(
                lambda: self.delete_zone(zone.id)
            )

        self.zones[zone.id] = zone_item

        for alarm in zone.alarms:
            self.add_alarm(zone, alarm)

        self.clearSelection()
        zone_item.setSelected(True)

        return zone_item

    def add_alarm(self, zone: Zone, alarm: ZoneAlarm):
        zone_item = self.zones[zone.id]
        alarm_item = self._new_row(alarm.name, self.EntryType.ALARM)

        zone_item.addChild(alarm_item)

        self._add_trash_button(alarm_item)

        alarm_item.trash_button.clicked.connect(
            lambda: self.delete_alarm(zone.id, alarm.id)
        )

        self.alarms[alarm.id] = alarm_item

        self.clearSelection()
        zone_item.setExpanded(True)
        alarm_item.setSelected(True)

    @pyqtSlot(int)
    def delete_zone(self, zone_id: int):

        # Delete zone from database
        if zone_id is not None:
            api.delete_zone(zone_id)

        # Delete the zone ZoneListItem from tree
        self.takeTopLevelItem(self.indexOfTopLevelItem(self.zones[zone_id]))

    @pyqtSlot(int, int)
    def delete_alarm(self, zone_id: int, alarm_id: int):

        zone_item = self.zones[zone_id]
        alarm_item = self.alarms[alarm_id]

        # Delete alarm from database
        api.delete_zone_alarm(alarm_id)

        # Delete the alarm ZoneListItem from tree
        zone_item.removeChild(alarm_item)

    def update_zone_type(self, zone_id: int, entry_type: EntryType):
        zone_item = self.zones[zone_id]
        icon = self._get_item_icon(entry_type)

        zone_item.setIcon(0, icon)

    def _new_row(self, name, entry_type: EntryType):
        row = ZoneListItem(["", name, ""])
        row.setIcon(0, self._get_item_icon(entry_type))

        return row

    def _get_item_icon(self, entry_type: EntryType):

        if entry_type == self.EntryType.REGION:
            entry_type_icon = QIcon(":/icons/region")
        elif entry_type == self.EntryType.LINE:
            entry_type_icon = QIcon(":/icons/line")
        elif entry_type == self.EntryType.ALARM:
            entry_type_icon = QIcon(":/icons/alarm")
        else:  # includes self.EntryType.UNKNOWN
            entry_type_icon = QIcon(":/icons/question_mark")

        return entry_type_icon

    def _add_trash_button(self, row_item: ZoneListItem):
        trash_button = QPushButton()
        trash_button.setIcon(QIcon(":/icons/trash"))
        self.setItemWidget(row_item, 2, trash_button)

        row_item.trash_button = trash_button


class ZoneListItemDelegate(QStyledItemDelegate):

    def __init__(self, *, row_height):
        super().__init__()

        self.row_height = row_height

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
        size_hint = super().sizeHint(option, index)
        size_hint.setHeight(self.row_height)

        return size_hint
