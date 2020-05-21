import logging
from typing import Dict, List

from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget

from brainframe.client.api_utils import api
from brainframe.api import bf_codecs
from brainframe.client.api_utils.zss_pubsub import zss_publisher
from brainframe.client.ui.resources import QTAsyncWorker
from brainframe.client.ui.main_window.video_thumbnail_view \
    .thumbnail_grid_layout.video_small.video_small import VideoSmall
from brainframe.client.ui.main_window.video_thumbnail_view \
    .video_thumbnail_view_ui import _VideoThumbnailViewUI


class VideoThumbnailView(_VideoThumbnailViewUI):
    stream_clicked = pyqtSignal(bf_codecs.StreamConfiguration)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.update_streams()

        self._init_signals()

    def _init_signals(self):

        self.alert_stream_layout.thumbnail_stream_clicked_signal.connect(
            self.stream_clicked)
        self.alertless_stream_layout.thumbnail_stream_clicked_signal.connect(
            self.stream_clicked)

    def _init_alert_pubsub(self):
        """Called after streams are initially populated"""
        stream_sub = zss_publisher.subscribe_alerts(self._handle_alerts)
        self.destroyed.connect(lambda: zss_publisher.unsubscribe(stream_sub))

    def update_streams(self):

        def on_success(stream_confs: List[bf_codecs.StreamConfiguration]):
            for stream_conf in stream_confs:
                self.add_stream_conf(stream_conf)

            self._init_alert_pubsub()

        QTAsyncWorker(self, api.get_stream_configurations,
                      on_success=on_success,
                      on_error=self._handle_get_stream_conf_error) \
            .start()

    @property
    def streams(self) -> Dict[int, VideoSmall]:
        alert_streams = self.alert_stream_layout.stream_widgets
        alertless_streams = self.alertless_stream_layout.stream_widgets

        all_streams = {**alert_streams, **alertless_streams}

        return all_streams

    def show_background_image(self, show_background: bool):
        self.scroll_area.setHidden(show_background)
        self.background_widget.setVisible(show_background)

    def add_stream_conf(self, stream_conf: bf_codecs.StreamConfiguration):
        self.alertless_stream_layout.new_stream_widget(stream_conf)

        self.show_background_image(False)

    def delete_stream_conf(self, stream_conf: bf_codecs.StreamConfiguration):
        stream_widget = self.streams[stream_conf.id]
        stream_widget.deleteLater()

        if len(self.streams) == 0:
            self.show_background_image(True)

    def expand_video_grids(self, expand):
        self.alertless_stream_layout.expand_grid(expand)
        self.alert_stream_layout.expand_grid(expand)

    def _handle_alerts(self, alerts: List[bf_codecs.Alert]):

        alert_streams = self.alert_stream_layout.stream_widgets
        alertless_streams = self.alertless_stream_layout.stream_widgets

        for alert in alerts:
            stream_id = alert.stream_id
            if stream_id not in self.streams:
                # Currently unsupported
                continue

            if alert.end_time is not None \
                    and stream_id not in alertless_streams:

                video_widget = self.alert_stream_layout.pop_stream_widget(
                    stream_id)
                self.alertless_stream_layout.add_video(video_widget)

            elif alert.end_time is None and stream_id not in alert_streams:

                video_widget = self.alertless_stream_layout.pop_stream_widget(
                    stream_id)
                self.alert_stream_layout.add_video(video_widget)

        streams_with_alerts = len(self.alert_stream_layout.stream_widgets) > 0
        self.alert_stream_layout.setVisible(streams_with_alerts)

    def _handle_get_stream_conf_error(self, exc: BaseException):

        message_title = self.tr("Error retrieving stream configurations")
        message = self.tr("Exception:")
        question = self.tr("Retry or Close Client?")
        message = (f"<{message}<br>"
                   f"<br>"
                   f"{exc}<br>"
                   f"<br>"
                   f"{question}")

        logging.error(message)

        buttons = QMessageBox.Retry | QMessageBox.Close
        ret_button = QMessageBox.question(self, message_title, message,
                                          buttons=buttons,
                                          defaultButton=QMessageBox.Retry)

        if ret_button is QMessageBox.Close:
            QApplication.instance().quit()
        else:
            # Retry again in 1 second. (Don't want to go to fast if holding
            # the escape key down or something)
            QTimer.singleShot(1000, self.update_streams)
