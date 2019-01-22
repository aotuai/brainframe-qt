from typing import Callable

from PyQt5.QtCore import Qt, QCoreApplication, QEvent, QSettings
from PyQt5.QtWidgets import QGraphicsView

from brainframe.shared.stream_listener import StreamListener
from brainframe.client.api import api
from brainframe.client.api.codecs import StreamConfiguration
from brainframe.client.api.streaming import SyncedStreamReader, ProcessedFrame
from brainframe.client.ui.resources.paths import image_paths
from brainframe.client.ui.dialogs.video_configuration import (
    VIDEO_SHOW_DETECTIONS,
    VIDEO_USE_POLYGONS,
    VIDEO_SHOW_DETECTION_LABELS,
    VIDEO_SHOW_ATTRIBUTES,
    VIDEO_SHOW_ZONES,
    VIDEO_SHOW_LINES
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
    draw_lines = True
    draw_regions = True
    draw_detections = True
    use_bounding_boxes = True
    show_labels = True
    show_attributes = True

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

        if self.settings.value(VIDEO_SHOW_LINES):
            self.scene().draw_lines(processed_frame.zone_statuses)

        if self.draw_regions:
            self.scene().draw_regions(processed_frame.zone_statuses)

        if self.draw_detections:
            self.scene().draw_detections(
                frame_tstamp=processed_frame.tstamp,
                tracks=processed_frame.tracks,
                use_bounding_boxes=self.use_bounding_boxes,
                show_labels=self.show_labels,
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
            if "VideoLarge" in str(type(self)):
                print("Init Event")
            self.handle_stream_initializing()
            return True
        elif event.type() == self.StreamHaltedEvent.event_type:
            if "VideoLarge" in str(type(self)):
                print("Halt Event")
            self.handle_stream_halted()
            return True
        elif event.type() == self.StreamClosedEvent.event_type:
            if "VideoLarge" in str(type(self)):
                print("Close Event")
            self.handle_stream_closed()
            return True
        elif event.type() == self.StreamErrorEvent:
            if "VideoLarge" in str(type(self)):
                print("Error Event")
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
