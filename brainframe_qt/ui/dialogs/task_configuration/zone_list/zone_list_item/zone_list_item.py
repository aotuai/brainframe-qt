from typing import List

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QTreeWidgetItem

from brainframe.api.bf_codecs import Zone, ZoneAlarm


class ZoneListItem(QTreeWidgetItem):

    def __init__(self, strings: List[str]):
        super().__init__(strings)

        self.zone: Zone = None
        self.alarm: ZoneAlarm = None

        self.edit_button = self._init_edit_button()
        self.trash_button = self._init_trash_button()

    def _init_edit_button(self) -> QPushButton:
        edit_button = QPushButton(self.parent())

        edit_button.setIcon(QIcon(":/icons/trash"))
        edit_button.setToolTip("Edit")

        return edit_button

    def _init_trash_button(self) -> QPushButton:
        trash_button = QPushButton(self.parent())

        trash_button.setIcon(QIcon(":/icons/trash"))
        trash_button.setToolTip("Delete")

        return trash_button
