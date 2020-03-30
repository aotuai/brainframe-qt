import functools
from typing import Dict, List, Union

from PyQt5.QtCore import QMargins, Qt, pyqtSlot, QThread, QMetaObject, Q_ARG
from PyQt5.QtWidgets import QLayout, QScrollArea, QVBoxLayout, QWidget

from brainframe.client.api import api
from brainframe.client.api.codecs import StreamConfiguration, Zone, ZoneAlarm
from brainframe.client.api.zss_pubsub import zss_publisher
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

        self._init_signals()

    def iterable_layout(self) -> QLayout:
        return self.widget().layout()

    def _init_signals(self):

        if self.bundle_mode == AlarmBundle.BundleType.BY_STREAM:
            sub = zss_publisher.subscribe_streams(self.handle_stream_id_stream)
        elif self.bundle_mode == AlarmBundle.BundleType.BY_ZONE:
            # TODO:
            sub = zss_publisher.subscribe_zones(self.handle_zone_stream)
        else:
            return

        self.destroyed.connect(lambda: zss_publisher.unsubscribe(sub))

    def create_bundle(self, bundle: Union[StreamConfiguration, Zone]) \
            -> AlarmBundle:
        """Create a new bundle with bundle_name and add it to the view"""
        alarm_bundle = AlarmBundle(self.bundle_mode, bundle, self)
        self.widget().layout().addWidget(alarm_bundle)
        self.bundle_map[bundle.id] = alarm_bundle
        return alarm_bundle

    def delete_bundle_by_id(self, bundle_id: int) -> None:
        alarm_bundle = self.bundle_map.pop(bundle_id)
        self.widget().layout().removeWidget(alarm_bundle)
        alarm_bundle.deleteLater()

    def get_bundle_id_for_alarm(self, alarm: ZoneAlarm) -> int:
        if self.bundle_mode == AlarmBundle.BundleType.BY_STREAM:
            return alarm.stream_id
        elif self.bundle_mode == AlarmBundle.BundleType.BY_ZONE:
            return alarm.zone_id
        else:
            raise NotImplementedError

    @pyqtSlot(object)
    def handle_stream_id_stream(self,
                                server_streams: List[StreamConfiguration]):
        """Add new alarms when the ZSS gets them"""

        if QThread.currentThread() != self.thread():
            # Move to the UI Thread
            QMetaObject.invokeMethod(self,
                                     self.handle_stream_id_stream.__name__,
                                     Qt.QueuedConnection,
                                     Q_ARG("PyQt_PyObject", server_streams))
            return

        server_stream_ids = {stream.id for stream in server_streams}

        new_stream_ids = server_stream_ids.difference(self.bundle_map)
        del_stream_ids = set(self.bundle_map).difference(server_stream_ids)

        # NOTE: THIS RELIES ON HACKS TO WORK. CURRENTLY THE StatusReceiver
        # SENDS _FAKE_ StreamConfigurations WITH JUST .id ATTRIBUTES SET
        for new_stream_id in new_stream_ids:
            # TODO: THIS API CALL IS SYNCHRONOUS WITH THE REST OF THE UI THREAD
            self.create_bundle(api.get_stream_configuration(new_stream_id))

        for del_alarm_id in del_stream_ids:
            self.delete_bundle_by_id(del_alarm_id)


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
