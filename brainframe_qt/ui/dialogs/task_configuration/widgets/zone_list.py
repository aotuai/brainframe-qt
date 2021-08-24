from typing import Dict

from PyQt5.QtCore import QModelIndex, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (
    QHeaderView,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QTreeWidget
)

from brainframe.api import bf_codecs

from brainframe_qt.api_utils import api

from ..core.zone import Zone, Line, Region
from .zone_list_item import ZoneListItem, ZoneListType


class ZoneList(QTreeWidget):
    initiate_zone_edit = pyqtSignal(int)
    zone_delete = pyqtSignal(int)

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

    def add_zone(self, zone: Zone) -> ZoneListItem:
        """Creates and returns the new ZoneListItem using the zone"""

        if isinstance(zone, Line):
            entry_type = ZoneListType.LINE
        elif isinstance(zone, Region):
            entry_type = ZoneListType.REGION
        else:
            entry_type = ZoneListType.UNKNOWN

        zone_item = self._new_row(zone.name, entry_type)
        self.addTopLevelItem(zone_item)

        self._init_zone_buttons(zone, zone_item)

        self.zones[zone.id] = zone_item

        for alarm in zone.alarms:
            self.add_alarm(zone, alarm)

        self.clearSelection()
        zone_item.setSelected(True)

        # zone_list_item = ZoneListItem(zone.name, entry_type)
        # zone_list_item.to_delete.connect(lambda: self.zone_delete.emit(zone.id))
        # zone_list_item.to_edit.connect(lambda: self.initiate_zone_edit.emit(zone.id))

        return zone_item

    def confirm_zone(self, zone: Zone) -> None:
        assert None in self.zones

        self.remove_zone(None)
        self.add_zone(zone)

    def add_alarm(self, zone: Zone, alarm: bf_codecs.ZoneAlarm):
        zone_item = self.zones[zone.id]
        alarm_item = self._new_row(alarm.name, ZoneListType.ALARM)

        zone_item.addChild(alarm_item)

        self._init_alarm_buttons(zone, alarm, alarm_item)

        self.alarms[alarm.id] = alarm_item

        self.clearSelection()
        zone_item.setExpanded(True)
        alarm_item.setSelected(True)

    @pyqtSlot(int, int)
    def delete_alarm(self, zone_id: int, alarm_id: int):

        zone_item = self.zones[zone_id]
        alarm_item = self.alarms[alarm_id]

        # Delete alarm from database
        api.delete_zone_alarm(alarm_id)

        # Delete the alarm ZoneListItem from tree
        zone_item.removeChild(alarm_item)

    def update_zone_type(self, zone_id: int, entry_type: ZoneListType):
        zone_item = self.zones[zone_id]
        icon = ZoneListItem.get_icon(entry_type)

        zone_item.setIcon(0, icon)

    def remove_zone(self, zone_id: int) -> None:
        self.takeTopLevelItem(self.indexOfTopLevelItem(self.zones[zone_id]))

    def _new_row(self, name, entry_type: ZoneListType):
        row = ZoneListItem(["", name, "", ""])

        icon = ZoneListItem.get_icon(entry_type)
        row.setIcon(0, icon)

        return row

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
            zone_item.trash_button.clicked.connect(
                lambda: self.zone_delete.emit(zone.id)
            )
            zone_item.edit_button.clicked.connect(
                lambda: self.initiate_zone_edit.emit(zone.id)
            )


class ZoneListItemDelegate(QStyledItemDelegate):

    def __init__(self, *, row_height):
        super().__init__()

        self.row_height = row_height

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
        size_hint = super().sizeHint(option, index)
        size_hint.setHeight(self.row_height)

        return size_hint
