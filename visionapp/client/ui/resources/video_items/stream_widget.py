import logging
from time import time

# noinspection PyUnresolvedReferences
# pyqtProperty is erroneously detected as unresolved
from PyQt5.QtCore import pyqtProperty, Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView

from visionapp.client.ui.resources.video_items import \
    StreamPolygon
from visionapp.client.ui.resources.video_items import DetectionPolygon, ZoneStatusPolygon
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

        # Stream configuration for current widget
        self.stream_conf = None

        # Render settings
        self.render_detections = True
        self.render_zones = True

        # Scene to draw items to
        self.scene_ = QGraphicsScene()
        self.setScene(self.scene_)

        self.video_stream = None  # Set in change_stream
        self.current_frame = None
        self._default_frame = QPixmap(str(image_paths.video_not_found))
        self.timestamp = -1

        self._frame_rate = frame_rate

        self.frame_update_timer = QTimer()
        # noinspection PyUnresolvedReferences
        # .connect is erroneously detected as unresolved
        self.frame_update_timer.timeout.connect(self.update_items)

        # Initialize stream configuration and get started
        self.change_stream(stream_conf)

        # Get the Status poller
        # TODO: Alex Uncomment
        self.status_poller = api.get_status_poller()

    def update_items(self):
        self.update_frame()
        self.update_latest_zones()
        self.update_latest_detections()

    def update_frame(self, pixmap: QPixmap = None):
        """Grab the newest frame from the Stream object

        :param pixmap: If passed, the frame will be manually set to it"""

        if not pixmap:
            # Check if the object actually has a stream
            if self.video_stream is None or \
                    not self.video_stream.is_initialized or \
                    not self.video_stream.is_running:
                # Since the video isn't working, clear any zones and dets
                self.remove_items_by_type(ZoneStatusPolygon)
                self.remove_items_by_type(DetectionPolygon)
                self._set_frame(self._default_frame)
                return

            timestamp, frame = self.video_stream.latest_frame_rgb

            # Don't render image if it hasn't changed
            if timestamp <= self.timestamp:
                return

            self.timestamp = timestamp
            pixmap = self._get_pixmap_from_numpy_frame(frame)
            self._set_frame(pixmap)
            # TODO: Use video_stream.is_running to stop widget if stream ends

    def update_latest_zones(self):
        if not self.render_zones: return
        self.remove_items_by_type(ZoneStatusPolygon)

        # Add new StreamPolygons
        statuses = self.status_poller.get_latest_statuses(self.stream_conf.id)

        for zone_status in statuses:
            if zone_status.zone.name == "Screen": continue
            self.scene_.addItem(ZoneStatusPolygon(zone_status))

    def update_latest_detections(self):
        self.remove_items_by_type(DetectionPolygon)
        if not self.render_detections: return

        # This function allows for fading out as well, though
        tstamp, dets = self.status_poller.get_detections(self.stream_conf.id)
        for det in dets:
            age = time() - tstamp
            polygon = DetectionPolygon(det, seconds_old=age)
            self.scene_.addItem(polygon)

    def change_stream(self, stream_conf):
        """Change the stream source of the video

        If stream_conf is None, the StreamWidget will stop grabbing frames"""
        self.stream_conf = stream_conf

        for item in self.scene_.items():
            self.scene_.removeItem(item)
            self.current_frame = None

        if not stream_conf:
            self._set_frame(QPixmap(str(image_paths.video_not_found)))
            self.frame_update_timer.stop()
        else:
            self.video_stream = api.get_stream_reader(stream_conf.id)
            self.frame_update_timer.start(1000 // self._frame_rate)

    def set_render_settings(self, *, detections=None, zones=None):
        if detections is not None:
            self.render_detections = detections
        if zones is not None:
            self.render_zones = zones

    def _set_frame(self, pixmap: QPixmap):
        """Set the current frame to the given pixmap"""
        # Create new QGraphicsPixmapItem if there isn't one
        if not self.current_frame:
            self.current_frame = self.scene_.addPixmap(pixmap)

        # Otherwise modify the existing one
        else:
            self.current_frame.setPixmap(pixmap)
        self.fitInView(self.scene_.itemsBoundingRect(), Qt.KeepAspectRatio)

    def remove_items_by_type(self, item_type):
        # Find current zones polygons
        items = self.scene_.items()
        polygons = filter(lambda item: type(item) == item_type, items)

        # Delete current zones polygons
        for polygon in polygons:
            self.scene_.removeItem(polygon)

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