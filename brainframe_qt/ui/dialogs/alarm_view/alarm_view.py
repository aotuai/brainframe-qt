import enum
from enum import Enum
from typing import Dict, List, Optional, Set

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLayout, QScrollArea, QVBoxLayout, QWidget

from brainframe.client.api import api
from brainframe.client.api.codecs import ZoneAlarm
from brainframe.client.ui.resources import QTAsyncWorker, stylesheet_watcher
from brainframe.client.ui.resources.alarms.alarm_bundle import AlarmBundle
from brainframe.client.ui.resources.mixins.data_structure import IterableMI
from brainframe.client.ui.resources.paths import qt_qss_paths


class AlarmViewUI(QScrollArea):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.container_widget = self._init_container_widget()
        self._init_viewport_widget()

        self._init_layout()

        self.setWidget(self.container_widget)

        self._init_style()

    def _init_layout(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.setAlignment(Qt.AlignTop)

        self.container_widget.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.container_widget.setAttribute(Qt.WA_StyledBackground, True)

        self.setWidgetResizable(True)

        stylesheet_watcher.watch(self, qt_qss_paths.alarm_view_qss)

    def _init_container_widget(self) -> QWidget:
        container_widget = QWidget(self)
        container_widget.setObjectName("container")
        return container_widget

    def _init_viewport_widget(self) -> None:
        # Give the viewport a name for the stylesheet
        self.viewport().setObjectName("viewport")


class AlarmView(AlarmViewUI, IterableMI):
    class BundleType(Enum):
        BY_STREAM = enum.auto()
        BY_ZONE = enum.auto()

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.bundle_mode = self.BundleType.BY_STREAM
        self.bundle_map: Dict[str, AlarmBundle] = {}

        QTAsyncWorker(self, self.get_alarm_info,
                      on_success=self.update_alarms,
                      on_error=self.update_alarms_err) \
            .start()

    def iterable_layout(self) -> QLayout:
        return self.container_widget.layout()

    def get_alarm_info(self):
        alarms = api.get_zone_alarms()
        # zones = {zone.id: zone for zone in api.get_zones()}
        # streams = {stream.id: stream
        #            for stream in api.get_stream_configurations()}

        return alarms

    def update_alarms(self, alarms: List[ZoneAlarm]):

        server_alarms = {alarm.id: alarm for alarm in alarms}
        local_alarms = {alarm.id: alarm for alarm in self.all_alarms}

        new_alarm_ids = set(server_alarms).difference(local_alarms)
        del_alarm_ids = set(local_alarms).difference(server_alarms)

        new_alarms = {alarm_id: server_alarms[alarm_id]
                      for alarm_id in new_alarm_ids}
        del_alarms = {alarm_id: local_alarms[alarm_id]
                      for alarm_id in del_alarm_ids}

        for new_alarm in new_alarms.values():
            self.add_alarm(new_alarm)

        for del_alarm in del_alarms.values():
            self.remove_alarm(del_alarm)

    def update_alarms_err(self, err: Exception):
        if not isinstance(err, requests.exceptions.ConnectionError):
            raise err

        print("ConnectionError: Unable to get alarms")

    def add_alarm(self, new_alarm: ZoneAlarm):
        """Create an AlarmCard for an alarm and add it to the correct
        AlarmBundle. Create the bundle if it does not already exist."""
        bundle = self._get_bundle_for_alarm(new_alarm)
        if not bundle:
            bundle_name = self._get_bundle_name_for_alarm(new_alarm)
            bundle = self.create_bundle(bundle_name)
        bundle.add_alarm_card(new_alarm)

    def remove_alarm(self, del_alarm: ZoneAlarm):
        """Remove an alarm's AlarmCard for its bundle"""
        bundle = self._get_bundle_for_alarm(del_alarm)
        bundle.del_alarm_card(del_alarm)

    def create_bundle(self, bundle_name):
        """Create a new bundle with bundle_name and add it to the view"""
        bundle = AlarmBundle(bundle_name, self)
        self.container_widget.layout().addWidget(bundle)
        self.bundle_map[bundle_name] = bundle
        return bundle

    @property
    def all_alarms(self) -> Set[ZoneAlarm]:
        return {alarm_card.alarm
                for bundle in self
                for alarm_card in bundle}

    def _create_bundle_for_alarm(self, alarm: ZoneAlarm):
        """Create a new bundle for an Alarm"""
        bundle_name = self._get_bundle_name_for_alarm(alarm)
        self.create_bundle(bundle_name)

    def _get_bundle_for_alarm(self, alarm: ZoneAlarm) -> Optional[AlarmBundle]:
        """Return the first bundle that matches the search criterion.
        Otherwise, returns None"""

        bundle_name = self._get_bundle_name_for_alarm(alarm)
        return self.bundle_map.get(bundle_name)

    def _get_bundle_name_for_alarm(self, alarm: ZoneAlarm) -> str:
        if self.bundle_mode == self.BundleType.BY_STREAM:
            return alarm.stream_id
        elif self.bundle_mode == self.BundleType.BY_ZONE:
            return alarm.zone_id
        else:
            raise NotImplementedError


if __name__ == '__main__':
    import typing
    from PyQt5.QtWidgets import QApplication

    api.set_url("http://localhost")

    app = QApplication([])
    app.setAttribute(Qt.AA_EnableHighDpiScaling)

    window = QWidget()
    window.setAttribute(Qt.WA_StyledBackground, True)

    window.setLayout(QVBoxLayout())
    window.layout().addWidget(AlarmView(typing.cast(QWidget, None)))

    window.show()

    app.exec_()
