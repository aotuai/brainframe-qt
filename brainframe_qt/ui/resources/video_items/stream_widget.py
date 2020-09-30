from typing import Callable

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QGraphicsView
from brainframe.api.bf_codecs import StreamConfiguration
from brainframe.api.bf_errors import StreamConfigNotFoundError, \
    StreamNotOpenedError

from brainframe.client.api_utils import api
from brainframe.client.api_utils.streaming import StreamListener, \
    SyncedStreamReader
# noinspection PyUnresolvedReferences
from brainframe.client.ui.resources import QTAsyncWorker, qt_resources, \
    settings
from brainframe.client.ui.resources.config import QSettingsRenderConfig
from .stream_graphics_scene import StreamGraphicsScene


class StreamWidget(QGraphicsView):
    """Base widget that uses Stream object to get frames.

    Makes use of a QTimer to get frames
    """
    # Type hint that self.scene() is more than just a QGraphicsScene
    scene: Callable[[], StreamGraphicsScene]

    def __init__(self, stream_conf, parent=None):
        # Order matters here, unfortunately
        super().__init__(parent)

        self.render_config = QSettingsRenderConfig()

        # Remove ugly white background and border from QGraphicsView
        self.setStyleSheet("background-color: transparent; border: 0px")

        # Scene to draw items to
        scene = StreamGraphicsScene(
            render_config=self.render_config,
            parent=self
        )
        self.setScene(scene)

        self.stream_listener = StreamListener()
        self.stream_reader: SyncedStreamReader = None  # Set in change_stream
        self.change_stream(stream_conf)

        self.startTimer(1000 // 30)

    def timerEvent(self, a0):
        if self.stream_listener.frame_event.is_set():
            self.stream_listener.frame_event.clear()
            self.handle_frame()

        if self.stream_listener.stream_initializing_event.is_set():
            self.stream_listener.stream_initializing_event.clear()
            self.handle_stream_initializing()

        if self.stream_listener.stream_halted_event.is_set():
            self.stream_listener.stream_halted_event.clear()
            self.handle_stream_halted()

        if self.stream_listener.stream_closed_event.is_set():
            self.stream_listener.stream_closed_event.clear()
            self.handle_stream_closed()

        if self.stream_listener.stream_error_event.is_set():
            self.stream_listener.stream_error_event.clear()
            self.handle_stream_error()

    def handle_frame(self):
        processed_frame = self.stream_reader.latest_processed_frame

        self.scene().remove_all_items()
        self.scene().set_frame(frame=processed_frame.frame)

        if self.render_config.draw_lines:
            self.scene().draw_lines(processed_frame.zone_statuses)

        if self.render_config.draw_regions:
            self.scene().draw_regions(processed_frame.zone_statuses)

        if self.render_config.draw_detections:
            self.scene().draw_detections(
                frame_tstamp=processed_frame.tstamp,
                tracks=processed_frame.tracks
            )

    def handle_stream_initializing(self):
        self.scene().remove_all_items()
        self.scene().set_frame(path=":/images/connecting_to_stream_png")
        ...

    def handle_stream_halted(self):
        self.scene().remove_all_items()
        self.scene().set_frame(path=":/images/connection_lost_png")

    def handle_stream_closed(self):
        self.handle_stream_halted()

    def handle_stream_error(self):
        self.scene().remove_all_items()
        self.scene().set_frame(path=":/images/error_message_png")

    def change_stream(self, stream_conf: StreamConfiguration):

        # When we no longer want to use a StreamWidget for an active stream
        if not stream_conf:
            self._clear_current_stream_reader()

            # Typically a user shouldn't see this, but sometimes the client is
            # laggy in closing the widget, so we don't use the error message
            self.handle_stream_closed()
            return

        def get_stream_url():
            try:
                return api.get_stream_url(stream_conf.id)
            except (StreamConfigNotFoundError, StreamNotOpenedError):
                return None

        def subscribe_to_stream_reader(stream_url: str):
            if stream_url is None:
                # Occurs when the get_stream_url() call fails due to
                # the stream having been deleted
                return None

            # Create the stream reader
            stream_reader = api.get_stream_manager().start_streaming(
                stream_conf, stream_url)

            # Inside of callback to avoid race conditions
            self._clear_current_stream_reader()

            if stream_reader is None:
                # This will happen if we try to get a StreamReader for a stream
                # that no longer exists, for example if a user clicks to expand
                # a stream the very instant before it's deleted from the server
                # We don't want to do anything
                return

            # Subscribe to the StreamReader
            self.stream_listener = StreamListener()
            self.stream_reader = stream_reader
            self.stream_reader.add_listener(self.stream_listener)

            # Make sure video is unsubscribed before it is GCed
            remove_listener = lambda: self.stream_reader.remove_listener(
                self.stream_listener)
            # noinspection PyUnresolvedReferences
            self.destroyed.connect(remove_listener)

        QTAsyncWorker(self, get_stream_url,
                      on_success=subscribe_to_stream_reader) \
            .start()

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

        current_frame = self.scene().current_frame

        if current_frame is not None:
            # EXTREMELY IMPORTANT LINE!
            # The sceneRect grows but never shrinks automatically
            self.scene().setSceneRect(current_frame.boundingRect())
            self.fitInView(current_frame.boundingRect(), Qt.KeepAspectRatio)

    def _clear_current_stream_reader(self):
        # If we currently have a stream reader, unsubscribe its listener
        # and clear any posted events
        if self.stream_reader:
            # noinspection PyUnresolvedReferences
            self.destroyed.disconnect()
            self.stream_reader.remove_listener(self.stream_listener)
            QCoreApplication.removePostedEvents(self)

            self.stream_reader = None
