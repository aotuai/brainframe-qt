from typing import List

from PyQt5.QtWidgets import QPushButton, QTreeWidgetItem

from brainframe.api.codecs import Zone, ZoneAlarm


class ZoneListItem(QTreeWidgetItem):

    def __init__(self, strings: List[str]):
        super().__init__(strings)

        self.zone: Zone = None
        self.alarm: ZoneAlarm = None

        self.trash_button: QPushButton = None

