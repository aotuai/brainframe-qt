from enum import Enum, auto
from typing import List

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QTreeWidgetItem

from brainframe.api.bf_codecs import Zone, ZoneAlarm


class ZoneListType(Enum):
    REGION = auto()
    LINE = auto()
    ALARM = auto()
    UNKNOWN = auto()


class ZoneListItem(QTreeWidgetItem):

    _ICON_MAP = {
        ZoneListType.REGION: QIcon(":/icons/region"),
        ZoneListType.LINE: QIcon(":/icons/line"),
        ZoneListType.ALARM: QIcon(":/icons/alarm"),
        ZoneListType.UNKNOWN: QIcon(":/icons/question_mark"),
    }

    def __init__(self, strings: List[str]):
        super().__init__(strings)

        self.zone: Zone = None
        self.alarm: ZoneAlarm = None

        self.edit_button = self._init_edit_button()
        self.trash_button = self._init_trash_button()

    def _init_edit_button(self) -> QPushButton:
        edit_button = QPushButton(self.parent())

        edit_button.setIcon(QIcon(":/icons/edit"))
        edit_button.setToolTip("Edit")

        return edit_button

    def _init_trash_button(self) -> QPushButton:
        trash_button = QPushButton(self.parent())

        trash_button.setIcon(QIcon(":/icons/trash"))
        trash_button.setToolTip("Delete")

        return trash_button

    @classmethod
    def get_icon(cls, entry_type: ZoneListType) -> QIcon:
        if entry_type not in cls._ICON_MAP:
            entry_type = ZoneListType.UNKNOWN
        return cls._ICON_MAP[entry_type]
