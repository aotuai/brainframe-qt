from typing import Optional

from PyQt5.QtCore import QCoreApplication, QTimer, QObject, pyqtSignal

from brainframe.api import bf_codecs, bf_errors

from brainframe_qt.api_utils import api
from brainframe_qt.api_utils.streaming import StreamListener, SyncedStreamReader
from brainframe_qt.api_utils.streaming.zone_status_frame import ZoneStatusFrame
from brainframe_qt.ui.resources import QTAsyncWorker


class StreamEventManager(StreamListener):

    stream_initializing = pyqtSignal()
    stream_halted = pyqtSignal()
    stream_closed = pyqtSignal()
    stream_error = pyqtSignal()

    frame_received = pyqtSignal(ZoneStatusFrame)

    def __init__(self, *, parent: QObject):
        StreamListener.__init__(self, parent=parent)

        self.stream_conf: Optional[bf_codecs.StreamConfiguration] = None
        """Current stream configuration used by the StreamReader"""

        self.stream_reader: Optional[SyncedStreamReader] = None

        self._has_alerts: bool = False

        self._frame_event_timer = QTimer()
        self._frame_event_timer.timeout.connect(self.check_for_frame_events)
        self._frame_event_timer.start(1000 // 30)  # ~30 FPS

    @property
    def latest_frame(self) -> ZoneStatusFrame:
        return self.stream_reader.latest_processed_frame

    def check_for_frame_events(self) -> None:
        if self.frame_event.is_set():
            self.frame_event.clear()

            frame = self.stream_reader.latest_processed_frame
            self.frame_received.emit(frame)

        if self.stream_initializing_event.is_set():
            self.stream_initializing_event.clear()

            self.stream_initializing.emit()

        if self.stream_halted_event.is_set():
            self.stream_halted_event.clear()

            self.stream_halted.emit()

        if self.stream_closed_event.is_set():
            self.stream_closed_event.clear()

            self.stream_closed.emit()

        if self.stream_error_event.is_set():
            self.stream_error_event.clear()

            self.stream_error.emit()

    def change_stream(self, stream_conf: bf_codecs.StreamConfiguration) -> None:

        # Clear the existing stream reader to get ready for a new one
        self._clear_current_stream_reader()
        self.stream_conf = stream_conf

        def handle_stream_url(stream_url: Optional[str]) -> None:
            # Occurs when the get_stream_url() call fails due to
            # the stream having been deleted
            if stream_url is None:
                return

            self._subscribe_to_stream(stream_conf, stream_url)

        QTAsyncWorker(self, self._get_stream_url, f_args=(stream_conf,),
                      on_success=handle_stream_url) \
            .start()

    def stop_streaming(self) -> None:
        self._clear_current_stream_reader()
        self.stream_conf = None

        self.stream_halted.emit()

    def _clear_current_stream_reader(self):
        """If we currently have a stream reader, unsubscribe its listener
        and clear any posted events"""

        # Ensure that we're not storing a stream_conf
        self.stream_conf = None

        if not self.stream_reader:
            return

        self.destroyed.disconnect()

        self.stream_reader.remove_listener(listener=self)

        # Make sure no more events are sent to this listener
        QCoreApplication.removePostedEvents(self)

        self.stream_reader = None

    def _subscribe_to_stream(self, stream_conf: bf_codecs.StreamConfiguration,
                             stream_url: str) \
            -> None:

        # Create the stream reader
        stream_reader = api.get_stream_manager() \
            .start_streaming(stream_conf, stream_url)

        if stream_reader is None:
            # This will happen if we try to get a StreamReader for a stream
            # that no longer exists, for example if a user clicks to expand
            # a stream the very instant before it's deleted from the server
            # We don't want to do anything
            return

        # Subscribe to the StreamReader
        self.stream_reader = stream_reader
        self.stream_reader.add_listener(listener=self)

        # Make sure video is unsubscribed before it is GCed
        self.destroyed.connect(
            lambda: self.stream_reader.remove_listener(listener=self))

    @staticmethod
    def _get_stream_url(stream_conf: bf_codecs.StreamConfiguration) \
            -> Optional[str]:
        try:
            return api.get_stream_url(stream_conf.id)
        except (
                bf_errors.StreamConfigNotFoundError,
                bf_errors.StreamNotOpenedError
        ):
            return None
