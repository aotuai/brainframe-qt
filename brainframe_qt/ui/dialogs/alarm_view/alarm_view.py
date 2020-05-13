from typing import Dict, List, Union

from PyQt5.QtCore import QMetaObject, QThread, Q_ARG, Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QLayout, QVBoxLayout, \
    QWidget

from brainframe.client.api_utils import api
from brainframe.api import StreamConfiguration, Zone, ZoneAlarm
from brainframe.client.api_utils.zss_pubsub import zss_publisher
from brainframe.client.ui.dialogs.alarm_view.alarm_view_ui import AlarmViewUI
from brainframe.client.ui.resources.alarms.alarm_bundle import AlarmBundle
from brainframe.client.ui.resources.mixins.data_structure import IterableMI


class AlarmView(AlarmViewUI, IterableMI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.bundle_mode = AlarmBundle.BundleType.BY_STREAM
        self.bundle_map: Dict[int, AlarmBundle] = {}
        """{object.id: AlarmBundle}"""

        self._init_signals()

    @classmethod
    def show_dialog(cls, parent):
        dialog = QDialog(parent)
        alarm_view = cls(dialog)

        window_title = QApplication.translate("AlarmView", "Alarm Status")
        dialog.setWindowTitle(window_title)
        dialog.setWindowFlags(Qt.Window)
        dialog.setLayout(QVBoxLayout())
        dialog.resize(600, 800)

        dialog.layout().addWidget(alarm_view)

        dialog.show()

    def iterable_layout(self) -> QLayout:
        return self.container_widget.layout()

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
        self.container_widget.layout().addWidget(alarm_bundle)
        self.bundle_map[bundle.id] = alarm_bundle

        # Ensure scroll area widget visible
        self.scroll_area.setVisible(True)
        self.background_widget.setHidden(True)

        return alarm_bundle

    def delete_bundle_by_id(self, bundle_id: int) -> None:
        alarm_bundle = self.bundle_map.pop(bundle_id)
        self.container_widget.layout().removeWidget(alarm_bundle)
        alarm_bundle.deleteLater()

        # Show the background image if there are no bundles
        no_bundles = (len(self.bundle_map) == 0)
        self.scroll_area.setHidden(no_bundles)
        self.background_widget.setVisible(no_bundles)

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
    from PyQt5.QtWidgets import QDesktopWidget

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
