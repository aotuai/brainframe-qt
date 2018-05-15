from typing import Tuple

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout
from PyQt5.uic import loadUi

from .zone_and_tasks import ZoneAndTasks
from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths


# TODO(Bryce Beagle): Scroll!
class ZoneList(QScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.zone_list_ui, self)

        self.stream_id = None
        self.zones = {}
        """Stores zones in a {zone.id: ZoneAndTasks()} dict"""

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

    def get_zones(self) -> Tuple[str]:
        """Get names of zones"""
        zones = self.zones.keys()

        # noinspection PyTypeChecker
        # PyCharm is dumb here
        return tuple(zones)

    def add_zone(self, zone):
        zone_widget = ZoneAndTasks(zone, self)
        self.zones[zone.id] = zone_widget
        self.main_layout.addWidget(zone_widget)

        for alarm in zone.alarms:
            self.add_alarm(zone, alarm)

        return zone_widget

    @pyqtSlot(int)
    def delete_zone(self, zone_id):
        api.delete_zone(self.stream_id, zone_id)
        self.delete_zone_widget(zone_id)

    def delete_zone_widget(self, zone_id):
        self.zones[zone_id].deleteLater()
        self.zones.pop(zone_id)

    def add_alarm(self, zone, alarm):
        """Add an alarm widget to a ZoneAndTasks widget"""
        self.zones[zone.id].add_alarm(alarm)

    def init_zones(self, stream_id):
        self.stream_id = stream_id
        zones = api.get_zones(stream_id)
        for zone in zones:
            zone_widget = self.add_zone(zone)  # type: ZoneAndTasks
            zone_widget.update_zone_type()
            self.zones[zone.id] = zone_widget
            zone_widget.zone_deleted_signal.connect(self.delete_zone)
