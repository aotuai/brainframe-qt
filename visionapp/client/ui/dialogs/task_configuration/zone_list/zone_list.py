from typing import Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QWidget
from PyQt5.uic import loadUi

from ui.resources import client_paths

# TODO: Scroll!
class ZoneList(QScrollArea):

    def __init__(self, parent):
        super().__init__(parent)

        loadUi(client_paths.zone_list_ui, self)

        self.zones = {}

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

    def get_zones(self) -> Tuple[str]:
        """Get names of zones"""
        # TODO: [Global] is for global zone for now
        zones = list(self.zones.keys()) + ["[Global]"]

        # noinspection PyTypeChecker
        return tuple(zones)

    def add_zone(self, zone):
        self.zones[zone.zone_name] = zone
        self.main_layout.addWidget(zone)

    def add_alarm(self, alarm):
        zone = alarm.zone

        if zone != "[Global]":  # TODO: Better management of global zone
            self.zones[zone].add_alarm(alarm)

        self.main_layout.addWidget(QWidget())
