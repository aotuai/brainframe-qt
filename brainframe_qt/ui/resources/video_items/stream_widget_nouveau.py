from typing import Callable

from PyQt5.QtCore import Qt, QCoreApplication, QEvent, QSettings
from PyQt5.QtWidgets import QGraphicsView

from brainframe.shared.stream_listener import StreamListener
from brainframe.client.api import api
from brainframe.client.api.codecs import StreamConfiguration
from brainframe.client.api.streaming import SyncedStreamReader, ProcessedFrame
from brainframe.client.ui.resources.paths import image_paths
from brainframe.client.ui.dialogs.video_configuration import (
    VIDEO_DRAW_DETECTIONS,
    VIDEO_USE_POLYGONS,
    VIDEO_SHOW_DETECTION_LABELS,
    VIDEO_SHOW_ATTRIBUTES,
    VIDEO_DRAW_REGIONS,
    VIDEO_DRAW_LINES
)
from .stream_graphics_scene import StreamGraphicsScene


class CommonMetaclass(type(QGraphicsView), type(StreamListener)):
    """QObjects have their own metaclass which conflicts with the
    StreamListener's metaclass. This forces them to get along.

    https://stackoverflow.com/questions/28720217/multiple-inheritance-metaclass-conflict
    """


class StreamWidget(QGraphicsView, StreamListener, metaclass=CommonMetaclass):
    """Base widget that uses Stream object to get frames.

    Makes use of a QTimer to get frames
    """
    _draw_lines = None
    _draw_regions = None
    _draw_detections = None
    _use_polygons = None
    _show_detection_labels = None
    _show_attributes = None

    # Type hint that self.scene() is more than just a QGraphicsScene
    scene: Callable[[], StreamGraphicsScene]

    def __init__(self, stream_conf, parent=None):
        # Order matters here, unfortunately
        StreamListener.__init__(self)
        QGraphicsView.__init__(self, parent)

        # Remove ugly white background and border from QGraphicsView
        self.setStyleSheet("background-color: transparent; border: 0px")

        # Scene to draw items to
        self.setScene(StreamGraphicsScene())

        self.stream_reader: SyncedStreamReader = None  # Set in change_stream
        self.settings = QSettings()
        self.change_stream(stream_conf)

    def handle_frame(self, processed_frame: ProcessedFrame):

        self.scene().remove_all_items()

        self.scene().set_frame(frame=processed_frame.frame)

        if self.settings.value(VIDEO_DRAW_LINES):
            self.scene().draw_lines(processed_frame.zone_statuses)

        if self.draw_regions:
            self.scene().draw_regions(processed_frame.zone_statuses)

        if self.draw_detections:
            self.scene().draw_detections(
                frame_tstamp=processed_frame.tstamp,
                tracks=processed_frame.tracks,
                use_polygons=self.use_polygons,
                show_detection_labels=self.show_detection_labels,
                show_attributes=self.show_attributes
            )

    def handle_stream_initializing(self):
        self.scene().remove_all_items()
        self.scene().set_frame(path=image_paths.connecting_to_stream)
        ...

    def handle_stream_halted(self):
        self.scene().remove_all_items()
        self.scene().set_frame(path=image_paths.connection_lost)

    def handle_stream_closed(self):
        self.handle_stream_halted()

    def handle_stream_error(self):
        self.scene().remove_all_items()
        self.scene().set_frame(path=image_paths.error)

    def change_stream(self, stream_conf: StreamConfiguration):
        if not stream_conf:
            # User should never see this
            self.handle_stream_error()
            return

        if self.stream_reader:
            self.stream_reader.remove_listener(self)
            QCoreApplication.removePostedEvents(self)
        self.stream_reader = api.get_stream_reader(stream_conf)
        self.stream_reader.add_listener(self)

        # Make sure video is unsubscribed before it is GCed
        self.destroyed.disconnect()
        self.destroyed.connect(lambda:
                               self.stream_reader.remove_listener(self))

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

    # Overrides qt's
    def event(self, event: QEvent):
        if event.type() == self.FrameEvent.event_type:
            self.handle_frame(event.processed_frame)
            return True
        elif event.type() == self.StreamInitializingEvent.event_type:
            self.handle_stream_initializing()
            return True
        elif event.type() == self.StreamHaltedEvent.event_type:
            self.handle_stream_halted()
            return True
        elif event.type() == self.StreamClosedEvent.event_type:
            self.handle_stream_closed()
            return True
        elif event.type() == self.StreamErrorEvent:
            self.handle_stream_error()
            return True
        else:
            return super().event(event)

    def resizeEvent(self, event=None):
        """Take up entire width using aspect ratio of scene"""

        current_frame = self.scene().current_frame

        if current_frame is not None:
            # EXTREMELY IMPORTANT LINE!
            # The sceneRect grows but never shrinks automatically
            self.scene().setSceneRect(current_frame.boundingRect())
            self.fitInView(current_frame.boundingRect(), Qt.KeepAspectRatio)

    @property
    def draw_lines(self):
        if self._draw_lines is not None:
            return self._draw_lines

        return self.settings.value(VIDEO_DRAW_LINES)

    @draw_lines.setter
    def draw_lines(self, draw_lines):
        self._draw_lines = draw_lines

    @property
    def draw_regions(self):
        if self._draw_regions is not None:
            return self._draw_regions

        return self.settings.value(VIDEO_DRAW_REGIONS)

    @draw_regions.setter
    def draw_regions(self, draw_regions):
        self._draw_regions = draw_regions

    @property
    def draw_detections(self):
        if self._draw_detections is not None:
            return self._draw_detections

        return self.settings.value(VIDEO_DRAW_DETECTIONS)

    @draw_detections.setter
    def draw_detections(self, draw_detections):
        self._draw_detections = draw_detections

    @property
    def use_polygons(self):
        if self._use_polygons is not None:
            return self._use_polygons

        return self.settings.value(VIDEO_USE_POLYGONS)

    @use_polygons.setter
    def use_polygons(self, use_polygons):
        self._use_polygons = use_polygons

    @property
    def show_detection_labels(self):
        if self._show_detection_labels is not None:
            return self._show_detection_labels

        return self.settings.value(VIDEO_SHOW_DETECTION_LABELS)

    @show_detection_labels.setter
    def show_detection_labels(self, show_detection_labels):
        self._show_detection_labels = show_detection_labels

    @property
    def show_attributes(self):
        if self._show_attributes is not None:
            return self._show_attributes

        return self.settings.value(VIDEO_SHOW_ATTRIBUTES)

    @show_attributes.setter
    def show_attributes(self, show_attributes):
        self._show_attributes = show_attributes
