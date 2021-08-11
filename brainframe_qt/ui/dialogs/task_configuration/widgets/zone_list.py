from enum import Enum
from typing import Dict, List

from PyQt5.QtCore import QModelIndex, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QHeaderView,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QTreeWidget
)

from brainframe.api import bf_codecs

from brainframe_qt.api_utils import api
from brainframe_qt.ui.resources import QTAsyncWorker

from ..core.zone import Zone, Line, Region
from .zone_list_item import ZoneListItem


class ZoneList(QTreeWidget):
    EntryType = Enum('EntryType', "REGION LINE ALARM UNKNOWN")

    initiate_zone_edit = pyqtSignal(Zone)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.stream_id = None

        # Lookup table to get zone/alarm from id (used during deletion)
        self.zones: Dict[int, ZoneListItem] = {}
        self.alarms: Dict[int, ZoneListItem] = {}

        self.setColumnCount(4)

        self._init_style()

    def _init_style(self) -> None:
        # Item delegate is used to force a custom row height
        self.setItemDelegate(ZoneListItemDelegate(row_height=40))

        self.setHeaderHidden(True)

        # Scale columns in view
        self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)

    def init_zones(self, stream_id):
        """Initialize zone list with zones already in database"""
        self.stream_id = stream_id

        def get_zones() -> List[Zone]:
            api_zones = api.get_zones(stream_id)
            zones = list(map(Zone.from_api_zone, api_zones))

            return zones

        def add_zones(zones: List[Zone]):
            for zone in zones:
                self.add_zone(zone)

            self.clearSelection()

        QTAsyncWorker(self, get_zones, on_success=add_zones).start()

    def add_zone(self, zone: Zone) -> ZoneListItem:
        """Creates and returns the new ZoneListItem using the zone"""

        if isinstance(zone, Line):
            entry_type = self.EntryType.LINE
        elif isinstance(zone, Region):
            entry_type = self.EntryType.REGION
        else:
            entry_type = self.EntryType.UNKNOWN

        zone_item = self._new_row(zone.name, entry_type)
        self.addTopLevelItem(zone_item)

        self._init_zone_buttons(zone, zone_item)

        self.zones[zone.id] = zone_item

        for alarm in zone.alarms:
            self.add_alarm(zone, alarm)

        self.clearSelection()
        zone_item.setSelected(True)

        return zone_item

    def add_alarm(self, zone: Zone, alarm: bf_codecs.ZoneAlarm):
        zone_item = self.zones[zone.id]
        alarm_item = self._new_row(alarm.name, self.EntryType.ALARM)

        zone_item.addChild(alarm_item)

        self._init_alarm_buttons(zone, alarm, alarm_item)

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
        row = ZoneListItem(["", name, "", ""])
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

    def _init_alarm_buttons(
        self, zone: Zone, alarm: bf_codecs.ZoneAlarm, alarm_item: ZoneListItem
    ) -> None:
        self.setItemWidget(alarm_item, 2, alarm_item.edit_button)
        self.setItemWidget(alarm_item, 3, alarm_item.trash_button)
        alarm_item.trash_button.clicked.connect(
            lambda: self.delete_alarm(zone.id, alarm.id)
        )

    def _init_zone_buttons(self, zone: Zone, zone_item: ZoneListItem) -> None:
        self.setItemWidget(zone_item, 2, zone_item.edit_button)
        self.setItemWidget(zone_item, 3, zone_item.trash_button)

        if zone.name == bf_codecs.Zone.FULL_FRAME_ZONE_NAME:
            zone_item.trash_button.setDisabled(True)
            zone_item.edit_button.setDisabled(True)
        else:
            zone_item.trash_button.clicked.connect(lambda: self.delete_zone(zone.id))
            zone_item.edit_button.clicked.connect(
                lambda: self.initiate_zone_edit.emit(zone)
            )


class ZoneListItemDelegate(QStyledItemDelegate):

    def __init__(self, *, row_height):
        super().__init__()

        self.row_height = row_height

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
        size_hint = super().sizeHint(option, index)
        size_hint.setHeight(self.row_height)

        return size_hint
