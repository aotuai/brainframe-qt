from typing import Dict, List

from PyQt5.QtCore import QMetaObject, QThread, Q_ARG, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget

from brainframe.api.bf_codecs import Alert, StreamConfiguration

from brainframe_qt.api_utils import api, get_stream_manager
from brainframe_qt.api_utils.zss_pubsub import zss_publisher
from brainframe_qt.ui.resources import QTAsyncWorker

from .widgets.video_small import VideoSmall
from .video_thumbnail_view_ui import _VideoThumbnailViewUI


class VideoThumbnailView(_VideoThumbnailViewUI):
    stream_clicked = pyqtSignal(StreamConfiguration)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_signals()

        self._retrieve_remote_streams()

    def _init_signals(self) -> None:

        self.alert_stream_layout.thumbnail_stream_clicked_signal.connect(
            self.stream_clicked)
        self.alertless_stream_layout.thumbnail_stream_clicked_signal.connect(
            self.stream_clicked)
        self.alert_stream_layout.thumbnail_stream_clicked_signal.connect(
            self._refresh_active_streams)
        self.alertless_stream_layout.thumbnail_stream_clicked_signal.connect(
            self._refresh_active_streams)

    def _init_alert_pubsub(self):
        """Called after streams are initially populated"""
        stream_sub = zss_publisher.subscribe_alerts(self._handle_alerts)
        self.destroyed.connect(lambda: zss_publisher.unsubscribe(stream_sub))

    @property
    def streams(self) -> Dict[int, VideoSmall]:
        alert_streams = self.alert_stream_layout.stream_widgets
        alertless_streams = self.alertless_stream_layout.stream_widgets

        all_streams = {**alert_streams, **alertless_streams}

        return all_streams

    def show_background_image(self, show_background: bool) -> None:
        self.scroll_area.setHidden(show_background)
        self.background_widget.setVisible(show_background)

    def add_stream(self, stream_conf: StreamConfiguration) -> None:
        self.alertless_stream_layout.new_stream_widget(stream_conf)

        self.show_background_image(False)

    def expand_video_grids(self, expand) -> None:
        self.alertless_stream_layout.expand_grid(expand)
        self.alert_stream_layout.expand_grid(expand)

    def remove_stream(self, stream_conf: StreamConfiguration) -> None:
        # Figure out which layout the stream is in, and remove it
        for layout in [self.alert_stream_layout, self.alertless_stream_layout]:
            for stream_id, stream_widget in layout.stream_widgets.items():
                if stream_id == stream_conf.id:
                    widget = layout.pop_stream_widget(stream_id)
                    widget.deleteLater()
                    break
            # https://stackoverflow.com/a/654002/8134178
            else:
                continue
            break

        if len(self.streams) == 0:
            self.show_background_image(True)

    @pyqtSlot(object)  # This is here for QMetaObject.invokeMethod
    def _handle_alerts(self, alerts: List[Alert]) -> None:

        if QThread.currentThread() != self.thread():
            # Move to the UI Thread
            QMetaObject.invokeMethod(self, self._handle_alerts.__name__,
                                     Qt.QueuedConnection,
                                     Q_ARG("PyQt_PyObject", alerts))
            return

        alert_streams = self.alert_stream_layout.stream_widgets
        alertless_streams = self.alertless_stream_layout.stream_widgets

        for alert in alerts:
            stream_id = alert.stream_id
            if stream_id not in self.streams:
                # Currently unsupported
                continue

            if alert.end_time is not None and stream_id not in alertless_streams:
                video_widget = self.alert_stream_layout.pop_stream_widget(stream_id)

                video_widget.alerts_ongoing = False
                self.alertless_stream_layout.add_video(video_widget)

            elif alert.end_time is None and stream_id not in alert_streams:
                video_widget = self.alertless_stream_layout.pop_stream_widget(stream_id)

                video_widget.alerts_ongoing = True
                self.alert_stream_layout.add_video(video_widget)

        streams_with_alerts = len(self.alert_stream_layout.stream_widgets) > 0
        self.alert_stream_layout.setVisible(streams_with_alerts)

        # Make sure we remove any streams that got left behind, such as when
        # an alarm is deleted while an alert is active
        stream_ids_with_alerts = set(alert.stream_id for alert in alerts)

        abandoned_stream_ids = alert_streams.keys() - stream_ids_with_alerts
        for stream_id in abandoned_stream_ids:
            video_widget = self.alert_stream_layout.pop_stream_widget(stream_id)
            self.alertless_stream_layout.add_video(video_widget)

    def _refresh_active_streams(self, stream_conf: StreamConfiguration) -> None:
        get_stream_manager().resume_streaming(stream_conf.id)

    def _retrieve_remote_streams(self) -> None:

        def on_success(stream_confs: List[StreamConfiguration]) -> None:
            for stream_conf in stream_confs:
                self.add_stream(stream_conf)

            self._init_alert_pubsub()

        QTAsyncWorker(self, api.get_stream_configurations, on_success=on_success) \
            .start()
