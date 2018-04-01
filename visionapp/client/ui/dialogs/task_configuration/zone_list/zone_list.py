from enum import Enum
from typing import Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QWidget
from PyQt5.uic import loadUi

from .zone_and_tasks import ZoneAndTasks
from visionapp.client.api import api
from visionapp.client.ui.resources.paths import qt_ui_paths


# TODO: Scroll!
class ZoneList(QScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.zone_list_ui, self)

        self.zones = {}

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

    def get_zones(self) -> Tuple[str]:
        """Get names of zones"""
        zones = self.zones.keys()

        # noinspection PyTypeChecker
        return tuple(zones)

    def add_zone(self, zone):
        zone_widget = ZoneAndTasks(zone, self)
        self.zones[zone.name] = zone_widget
        self.main_layout.addWidget(zone_widget)

        for alarm in zone.alarms:
            self.add_alarm(zone, alarm)

        return zone_widget

    def add_alarm(self, zone, alarm):
        """Add an alarm widget to a ZoneAndTasks widget"""
        self.zones[zone.name].add_alarm(alarm)

    def init_zones(self, stream_id):
        zones = api.get_zones(stream_id)
        for zone in zones:
            self.zones[zone.name] = self.add_zone(zone)
