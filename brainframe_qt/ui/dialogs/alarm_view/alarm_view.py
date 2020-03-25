import enum
from enum import Enum
from typing import Dict, List, Optional, Set

from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtWidgets import QLayout, QScrollArea, QVBoxLayout, QWidget

from brainframe.client.api import api
from brainframe.client.api.codecs import StreamConfiguration, Zone, ZoneAlarm
from brainframe.client.ui.resources import QTAsyncWorker, stylesheet_watcher
from brainframe.client.ui.resources.alarms.alarm_bundle import AlarmBundle
from brainframe.client.ui.resources.mixins.data_structure import IterableMI
from brainframe.client.ui.resources.mixins.style import TransientScrollbarMI
from brainframe.client.ui.resources.paths import qt_qss_paths


class AlarmViewUI(QScrollArea, TransientScrollbarMI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        container_widget = self._init_container_widget()
        self._init_viewport_widget()

        self.setWidget(container_widget)

        self._init_style()

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setWidgetResizable(True)

        stylesheet_watcher.watch(self, qt_qss_paths.alarm_view_qss)

    def _init_container_widget(self) -> QWidget:
        container_widget = QWidget(self)
        container_widget.setObjectName("container")
        container_widget.setAttribute(Qt.WA_StyledBackground, True)

        # Leave some space on the right for the scrollbar
        contents_margins: QMargins = self.contentsMargins()
        contents_margins.setLeft(50)
        contents_margins.setRight(50)
        container_widget.setContentsMargins(contents_margins)

        container_widget.setLayout(self._init_container_widget_layout())

        return container_widget

    # noinspection PyMethodMayBeStatic
    def _init_container_widget_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.setAlignment(Qt.AlignTop)
        return layout

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
        self.bundle_map: Dict[int, AlarmBundle] = {}
        """{object.id: AlarmBundle}"""

        self._init_alarm_bundles()

    def iterable_layout(self) -> QLayout:
        return self.widget().layout()

    def _init_alarm_bundles(self):
        QTAsyncWorker(self, self.get_current_configuration,
                      on_success=self.populate_view,
                      on_error=self.handle_get_config_error) \
            .start()

    def get_current_configuration(self):
        streams = api.get_stream_configurations()
        zones = api.get_zones()
        alarms = api.get_zone_alarms()

        return streams, zones, alarms

    def populate_view(self, configuration):
        streams: List[StreamConfiguration]
        zones: List[Zone]
        alarms: List[ZoneAlarm]
        streams, zones, alarms = configuration

        # Create bundles
        if self.bundle_mode is self.BundleType.BY_STREAM:
            bundles_to_make = streams
        elif self.bundle_mode is self.BundleType.BY_ZONE:
            bundles_to_make = zones
        else:
            raise TypeError(f"Unknown bundle type {self.bundle_mode}")

        for bundle in bundles_to_make:
            # Create bundle if it does not already exist
            self.bundle_map.setdefault(bundle.id,
                                       self.create_bundle(bundle.name))

        # Create alarm cards
        for alarm in alarms:
            self.add_alarm(alarm)

    def handle_get_config_error(self, err):
        raise err

    # # For future use
    # def update_alarms(self, alarms: List[ZoneAlarm]):
    #
    #     server_alarms = {alarm.id: alarm for alarm in alarms}
    #     local_alarms = {alarm.id: alarm for alarm in self.all_alarms}
    #
    #     new_alarm_ids = set(server_alarms).difference(local_alarms)
    #     del_alarm_ids = set(local_alarms).difference(server_alarms)
    #
    #     new_alarms = {alarm_id: server_alarms[alarm_id]
    #                   for alarm_id in new_alarm_ids}
    #     del_alarms = {alarm_id: local_alarms[alarm_id]
    #                   for alarm_id in del_alarm_ids}
    #
    #     for new_alarm in new_alarms.values():
    #         self.add_alarm(new_alarm)
    #
    #     for del_alarm in del_alarms.values():
    #         self.remove_alarm(del_alarm)

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
        self.widget().layout().addWidget(bundle)
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
    from PyQt5.QtWidgets import QApplication, QDesktopWidget

    api.set_url("http://localhost")
    zss = api.get_status_receiver()

    # noinspection PyArgumentList
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication([])

    # noinspection PyArgumentList
    window = QWidget()
    window.setWindowFlags(Qt.WindowStaysOnTopHint)
    window.resize(QDesktopWidget().availableGeometry(window).size() * .4)
    window.setAttribute(Qt.WA_StyledBackground, True)

    window.setLayout(QVBoxLayout())
    window.layout().addWidget(AlarmView(typing.cast(QWidget, None)))

    window.show()

    app.exec_()
