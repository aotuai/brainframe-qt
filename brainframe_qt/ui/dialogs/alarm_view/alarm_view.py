import enum
from enum import Enum
from typing import Dict, List, Optional, Set, Union

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

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.bundle_mode = AlarmBundle.BundleType.BY_STREAM
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

        return streams, zones

    def populate_view(self, configuration):
        streams: List[StreamConfiguration]
        zones: List[Zone]
        streams, zones = configuration

        # Create bundles
        if self.bundle_mode is AlarmBundle.BundleType.BY_STREAM:
            bundles_to_make = streams
        elif self.bundle_mode is AlarmBundle.BundleType.BY_ZONE:
            bundles_to_make = zones
        else:
            raise TypeError(f"Unknown bundle type {self.bundle_mode}")

        for bundle in bundles_to_make:
            # Create bundle if it does not already exist
            self.bundle_map.setdefault(bundle.id, self.create_bundle(bundle))

    def handle_get_config_error(self, err):
        raise err

    def create_bundle(self, bundle: Union[StreamConfiguration, Zone]) \
            -> AlarmBundle:
        """Create a new bundle with bundle_name and add it to the view"""
        alarm_bundle = AlarmBundle(self.bundle_mode, bundle, self)
        self.widget().layout().addWidget(alarm_bundle)
        self.bundle_map[bundle.id] = alarm_bundle
        return alarm_bundle

    def delete_bundle(self, bundle_id: int) -> None:
        # TODO:
        ...

    def get_bundle_id_for_alarm(self, alarm: ZoneAlarm) -> int:
        if self.bundle_mode == AlarmBundle.BundleType.BY_STREAM:
            return alarm.stream_id
        elif self.bundle_mode == AlarmBundle.BundleType.BY_ZONE:
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
