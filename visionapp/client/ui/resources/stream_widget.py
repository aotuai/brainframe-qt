import logging

# noinspection PyUnresolvedReferences
# pyqtProperty is erroneously detected as unresolved
from PyQt5.QtCore import pyqtProperty, Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView

from visionapp.client.ui.resources.paths import image_paths
from visionapp.client.api import api


class StreamWidget(QGraphicsView):
    """Base widget that uses Stream object to get frames

    Makes use of a QTimer to get frames"""

    def __init__(self, stream_conf=None, frame_rate=30, parent=None):
        """Init StreamWidget object

        :param frame_rate: Frame rate of video in fps
        """
        super().__init__(parent)

        # Remove ugly white background and border from QGraphicsView
        self.setStyleSheet("background-color: transparent; border: 0px")

        self.stream_conf = None

        self.scene_ = QGraphicsScene()
        self.setScene(self.scene_)

        self.video_stream = None
        self.current_frame = None
        self.timestamp = -1

        self._frame_rate = frame_rate

        self.frame_update_timer = QTimer()
        # noinspection PyUnresolvedReferences
        # .connect is erroneously detected as unresolved
        self.frame_update_timer.timeout.connect(self.update_frame)

        # Initialize stream configuration and get started
        self.change_stream(stream_conf)

    def update_frame(self, pixmap: QPixmap = None):
        """Grab the newest frame from the Stream object

        :param pixmap: If passed, the frame will be manually set to it"""
        if not pixmap:
            if not self.video_stream.is_initialized:
                # Don't display a frame until stream is ready
                return

            timestamp, frame = self.video_stream.latest_frame_rgb

            # Don't render image if it hasn't changed
            if timestamp <= self.timestamp:
                return
            else:
                self.timestamp = timestamp

            pixmap = self._get_pixmap_from_numpy_frame(frame)
            # TODO: Use video_stream.is_running to stop widget if stream ends

        # Create new QGraphicsPixmapItem if there isn't one
        if not self.current_frame:
            self.current_frame = self.scene_.addPixmap(pixmap)

        # Otherwise modify the existing one
        else:
            self.current_frame.setPixmap(pixmap)
        self.fitInView(self.scene_.itemsBoundingRect(), Qt.KeepAspectRatio)

    # TODO
    def change_stream(self, stream_conf):
        """Change the stream source of the video

        If stream_conf is None, the StreamWidget will stop grabbing frames"""
        self.stream_conf = stream_conf

        for item in self.scene_.items():
            self.scene_.removeItem(item)
            self.current_frame = None

        if not stream_conf:
            self.update_frame(QPixmap(str(image_paths.video_not_found)))
            self.frame_update_timer.stop()
        else:
            self.video_stream = api.get_stream(stream_conf.id)
            self.frame_update_timer.start(1000 // self._frame_rate)

    @pyqtProperty(int)
    def frame_rate(self):
        return self._frame_rate

    @frame_rate.setter
    def frame_rate(self, frame_rate):
        self.frame_update_timer.setInterval(1000 // frame_rate)
        self._frame_rate = frame_rate

    @staticmethod
    def _get_pixmap_from_numpy_frame(frame):
        height, width, channel = frame.shape
        bytes_per_line = width * 3
        image = QImage(frame.data, width, height, bytes_per_line,
                       QImage.Format_RGB888)
        return QPixmap.fromImage(image)
