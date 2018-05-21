from collections import defaultdict
from time import time

# noinspection PyUnresolvedReferences
# pyqtProperty is erroneously detected as unresolved
from PyQt5.QtCore import pyqtProperty, Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView

from brainframe.client.ui.resources.video_items import (
    DetectionPolygon,
    ZoneStatusPolygon
)
from brainframe.client.ui.resources.paths import image_paths
from brainframe.client.api import api


class StreamWidget(QGraphicsView):
    """Base widget that uses Stream object to get frames.

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
        self.setScene(QGraphicsScene())

        self.video_stream = None  # Set in change_stream
        self.current_frame = None
        self.timestamp = -1

        self._frame_rate = frame_rate

        self.frame_update_timer = QTimer()
        # noinspection PyUnresolvedReferences
        # .connect is erroneously detected as unresolved
        self.frame_update_timer.timeout.connect(self.update_items)

        # Initialize stream configuration and get started
        self.change_stream(stream_conf)

        # Get the Status poller
        self.status_poller = api.get_status_poller()

        # For debugging. Easy to see true widget size
        # self.setStyleSheet("background-color:green;")

    def update_items(self):
        self.update_frame()
        self.update_latest_zones()
        self.update_latest_detections()

    def update_frame(self):
        """Grab the newest frame from the Stream object"""

        # Check if the object actually has a stream
        if self.video_stream is None:
            pixmap = self._static_pixmap(image_paths.stream_finished)
            self._set_frame(pixmap)
            return
        if not self.video_stream.is_running:
            pixmap = self._static_pixmap(image_paths.stream_finished)
            self._set_frame(pixmap)
            return
        if self.video_stream.is_running \
                and not self.video_stream.is_initialized:
            pixmap = self._static_pixmap(image_paths.connecting_to_stream)
            self._set_frame(pixmap)
            return

        frame = self.video_stream.latest_processed_frame_rgb
        if frame is not None:
            # Don't render image if it hasn't changed
            # if frame.tstamp <= self.timestamp:
                # return

            self.timestamp = frame.tstamp
            pixmap = self._get_pixmap_from_numpy_frame(frame.frame)
            self._set_frame(pixmap)
            # TODO(Bryce Beagle): Use video_stream.is_running to stop widget if
            # stream ends

    def update_latest_zones(self):
        self.remove_items_by_type(ZoneStatusPolygon)
        if not self.render_zones:
            return
        if not self.stream_is_up:
            return

        # Add new StreamPolygons
        frame = self.video_stream.latest_processed_frame_rgb
        if frame is not None:
            if frame.zone_status.zone.name == "Screen":
                return
            # Border thickness as % of screen size
            border = self.scene().width() / 100
            self.scene().addItem(ZoneStatusPolygon(frame.zone_status,
                                                   border_thickness=border))

    def update_latest_detections(self):
        self.remove_items_by_type(DetectionPolygon)
        if not self.render_detections or not self.stream_is_up:
            return

        frame = self.video_stream.latest_processed_frame_rgb
        if frame is not None:
            interested_attributes = defaultdict(set)
            for alarm in frame.zone_status.zone.alarms:
                for condition in alarm.count_conditions:

                    class_name = condition.with_class_name
                    attribute = condition.with_attribute

                    # Nothing to add if no attributes with alarm
                    if attribute is None:
                        continue

                    interested_attributes[class_name].add(attribute.value)

            for detection in frame.zone_status.detections:
                attributes = set(
                    attribute.value for attribute in detection.attributes)
                class_name = detection.class_name
                attributes_in_alarm = interested_attributes[class_name]

                attributes_to_draw = attributes.intersection(
                    attributes_in_alarm)

                age = time() - frame.tstamp  # Used for fading
                polygon = DetectionPolygon(detection,
                                           attributes=attributes_to_draw,
                                           seconds_old=age)
                self.scene().addItem(polygon)

    def change_stream(self, stream_conf):
        """Change the stream source of the video

        If stream_conf is None, the StreamWidget will stop grabbing frames"""
        self.stream_conf = stream_conf

        for item in self.scene().items():
            self.scene().removeItem(item)
            self.current_frame = None

        if not stream_conf:
            self._set_frame(QPixmap(str(image_paths.video_not_found)))
            self.frame_update_timer.stop()
        else:
            self.video_stream = api.get_stream_reader(stream_conf)
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
            self.current_frame = self.scene().addPixmap(pixmap)

        # Otherwise modify the existing one
        else:
            self.current_frame.setPixmap(pixmap)

        # Force resize
        self._resize(self.size())

    def remove_items_by_type(self, item_type):
        # Find current zones polygons
        items = self.scene().items()
        polygons = filter(lambda item: type(item) == item_type, items)

        # Delete current zones polygons
        for polygon in polygons:
            self.scene().removeItem(polygon)

    @property
    def stream_is_up(self):
        """Returns True if there is an active stream that is giving frames
        at the moment."""
        return self.video_stream is not None \
               and self.video_stream.is_initialized \
               and self.video_stream.is_running

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

    @staticmethod
    def _static_pixmap(path):
        return QPixmap(str(path))

    def resizeEvent(self, event=None):
        """Take up entire width using aspect ratio of scene"""
        self._resize(event.size())

    def _resize(self, size):

        if self.current_frame is not None:
            # EXTREMELY IMPORTANT LINE!
            # The sceneRect grows but never shrinks automatically
            self.scene().setSceneRect(self.current_frame.boundingRect())
            self.fitInView(self.current_frame.boundingRect(),
                           Qt.KeepAspectRatio)
