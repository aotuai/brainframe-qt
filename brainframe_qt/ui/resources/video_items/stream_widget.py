from collections import defaultdict

# noinspection PyUnresolvedReferences
# pyqtProperty is erroneously detected as unresolved
from PyQt5.QtCore import pyqtProperty, Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView

from brainframe.client.api import api
from brainframe.client.api.streaming import SyncedStreamReader
from brainframe.shared.stream_utils import StreamStatus
from brainframe.client.ui.resources.paths import image_paths
from brainframe.client.ui.resources.video_items import (
    DetectionPolygon,
    ZoneStatusPolygon
)


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
        # self.setFrameStyle(0)

        # Stream configuration for current widget
        self.stream_conf = None

        # Render settings
        self.render_detections = True
        self.render_zones = True

        # Scene to draw items to
        self.setScene(QGraphicsScene())

        self.video_stream: SyncedStreamReader = None  # Set in change_stream
        self.stream_status = None
        """Tracks the current known state of the stream and prevents redrawing
        if the state has not changed"""
        self.current_frame = None
        self.timestamp = -1

        self._frame_rate = frame_rate

        self.frame_size = None

        self.frame_update_timer = QTimer()
        # noinspection PyUnresolvedReferences
        self.frame_update_timer.timeout.connect(self.update_items)

        # Initialize stream configuration and get started
        self.change_stream(stream_conf)

        # Get the Status poller
        self.status_poller = api.get_status_poller()

        # For debugging. Easy to see true widget size
        # self.setStyleSheet("background-color:green;")

    def update_items(self):
        frame = self.video_stream.latest_processed_frame_rgb

        # Only update detections & zones when needed
        if self.stream_is_up and frame is not None:
            if frame.tstamp != self.timestamp:
                self.update_latest_zones(frame.zone_statuses)
                self.update_latest_detections(frame.zone_statuses)
        else:
            self.remove_items_by_type(DetectionPolygon)
            self.remove_items_by_type(ZoneStatusPolygon)

        self.update_frame()

    def update_frame(self):
        """Grab the newest frame from the Stream object"""

        # Check if the object actually has a stream
        if self.video_stream is None:
            pixmap = self._static_pixmap(image_paths.connection_lost)
            self._set_frame(pixmap)
            self.resizeEvent()
            return

        pixmap = None

        # Video is streaming frames
        if self.video_stream.status is StreamStatus.streaming:
            frame = self.video_stream.latest_processed_frame_rgb
            # Change image only we have a new one
            if frame and frame.tstamp > self.timestamp:
                self.timestamp = frame.tstamp
                pixmap = self._get_pixmap_from_numpy_frame(frame.frame)
                self._set_frame(pixmap)

        # Video is not streaming
        elif self.stream_status is not self.video_stream.status:
            if self.video_stream.status is StreamStatus.halted:
                pixmap = self._static_pixmap(image_paths.connection_lost)
            elif self.video_stream.status is StreamStatus.initializing:
                pixmap = self._static_pixmap(image_paths.connecting_to_stream)
            else:
                raise ValueError("Unknown stream status")

            self._set_frame(pixmap)

        # Update viewport if the frame size has changed
        if pixmap:
            if self.frame_size != pixmap.size():
                self.resizeEvent()
                self.updateGeometry()
            self.frame_size = pixmap.size()
        else:
            self.frame_size = None

        # Keep track of current stream_status to monitor changes
        self.stream_status = self.video_stream.status

    def update_latest_zones(self, zone_statuses):
        """Update the zones drawn on the frame"""
        self.remove_items_by_type(ZoneStatusPolygon)
        if not self.render_zones:
            return

        # Draw all of the zones (except the default zone, "screen")
        for zone_status in zone_statuses:
            if zone_status.zone.name != "Screen":
                # Border thickness as % of screen size
                border = self.scene().width() / 200
                self.scene().addItem(ZoneStatusPolygon(
                    zone_status,
                    text_size=int(self.scene().height() / 50),
                    border_thickness=border))

    def update_latest_detections(self, zone_statuses):
        """Update the detections drawn on the frame"""
        self.remove_items_by_type(DetectionPolygon)
        if not self.render_detections:
            return

        screen_zone_status = None  # The status with all Detections in it

        # Get attributes of interest
        interested_attributes = defaultdict(set)
        for zone_status in zone_statuses:
            if zone_status.zone.name == "Screen":
                screen_zone_status = zone_status

            for alarm in zone_status.zone.alarms:
                for condition in alarm.count_conditions:
                    class_name = condition.with_class_name
                    attribute = condition.with_attribute

                    # Nothing to add if no attributes with alarm
                    if attribute is None:
                        continue

                    interested_attributes[class_name].add(attribute.value)

        if not screen_zone_status:
            raise ValueError("A packet of ZoneStatuses must always include"
                             " one with the name 'Screen'")

        for detection in screen_zone_status.detections:
            attributes = set(attr.value for attr in detection.attributes)
            class_name = detection.class_name

            attributes_in_alarm = interested_attributes[class_name]
            attributes_to_draw = attributes.intersection(attributes_in_alarm)

            # Draw the detection on the screen
            polygon = DetectionPolygon(
                detection,
                text_size=int(self.scene().height() / 50),
                attributes=attributes_to_draw,
                seconds_old=0)  # Fading is currently disabled
            self.scene().addItem(polygon)

    def change_stream(self, stream_conf):
        """Change the stream source of the video

        If stream_conf is None, the StreamWidget will stop grabbing frames"""
        self.stream_conf = stream_conf

        for item in self.scene().items():
            self.scene().removeItem(item)
            self.current_frame = None

        if not stream_conf:
            # User should never see this image
            self._set_frame(QPixmap(str(image_paths.error)))
            self.frame_update_timer.stop()
        else:
            self.video_stream = api.get_stream_reader(stream_conf)

            # Reset timestamp so that a frame is always drawn. The old stream
            # may have had a newer frame than the new one.
            self.timestamp = -1

            # Run immediately then start timer
            self.update_items()
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

            # Fixes BF-319: Clicking a stream, closing it, and reopening it
            # again resulted in a stream that wasn't displayed properly. This
            # was because the resizeEvent() would be triggered before the frame
            # was set from None->'actual frame' preventing the setSceneRect()
            # from being called. The was not an issue if another stream was
            # clicked because it would then get _another_ resize event after the
            # frame was loaded because the frame size would be different.
            self.resizeEvent()

        # Otherwise modify the existing one
        else:
            self.current_frame.setPixmap(pixmap)

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
            and self.video_stream.status is StreamStatus.streaming

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

    def hasHeightForWidth(self):
        """Enable the use of heightForWidth"""
        return True

    def heightForWidth(self, width: int):
        """Lock the aspect ratio of the widget to match the aspect ratio of the
        scene and its video frame
        """

        if not self.scene().width():
            return 0

        return width * self.scene().height() / self.scene().width()

    def resizeEvent(self, event=None):
        """Take up entire width using aspect ratio of scene"""

        if self.current_frame is not None:
            # EXTREMELY IMPORTANT LINE!
            # The sceneRect grows but never shrinks automatically
            self.scene().setSceneRect(self.current_frame.boundingRect())
            self.fitInView(self.current_frame.boundingRect(),
                           Qt.KeepAspectRatio)
