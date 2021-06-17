from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal

from brainframe.api.bf_codecs import StreamConfiguration
from brainframe.api.bf_errors import StreamConfigNotFoundError, StreamNotOpenedError
from gstly.abstract_stream_reader import StreamStatus

from brainframe_qt.api_utils import api, get_stream_manager
from brainframe_qt.api_utils.streaming import StreamListener, SyncedStreamReader
from brainframe_qt.api_utils.streaming.zone_status_frame import ZoneStatusFrame
from brainframe_qt.ui.resources import QTAsyncWorker


class StreamEventManager(StreamListener):

    stream_initializing = pyqtSignal()
    stream_halted = pyqtSignal()
    stream_closed = pyqtSignal()
    stream_error = pyqtSignal()

    frame_received = pyqtSignal(ZoneStatusFrame)

    def __init__(self, stream_conf: StreamConfiguration, *, parent: QObject):
        super().__init__(self, parent=parent)

        self.stream_conf: StreamConfiguration = stream_conf
        self.stream_reader: Optional[SyncedStreamReader] = None

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

    def change_stream(self, stream_conf: Optional[StreamConfiguration]) -> None:

        # Clear the existing stream reader to get ready for a new one
        self._clear_current_stream_reader()
        self.stream_conf = stream_conf

        if not stream_conf:
            self._disconnect_stream_reader()
            self.stream_reader = None
            return

        def handle_stream_url(stream_url: Optional[str]) -> None:
            # Occurs when the get_stream_url() call fails due to
            # the stream having been deleted
            if stream_url is None:
                return

            # User must have already changed stream again by the time this callback is
            # called. Just forget about this current change request.
            if stream_conf is not self.stream_conf:
                return

            self._subscribe_to_stream(stream_conf, stream_url)

        QTAsyncWorker(self, self._get_stream_url, f_args=(stream_conf,),
                      on_success=handle_stream_url) \
            .start()

    def _on_state_change(self, state: StreamStatus) -> None:
        if state is StreamStatus.INITIALIZING:
            self.stream_initializing.emit()
        elif state is StreamStatus.HALTED:
            self.stream_halted.emit()
        elif state is StreamStatus.CLOSED:
            self.stream_closed.emit()
        elif state is StreamStatus.STREAMING:
            # Streaming, but no frame received yet
            self.stream_initializing.emit()
        else:
            self.stream_error.emit()

    def _subscribe_to_stream(
        self,
        stream_conf: StreamConfiguration,
        stream_url: str
    ) -> None:

        # Create the stream reader
        stream_manager = get_stream_manager()
        stream_reader = stream_manager.start_streaming(stream_conf, stream_url)

        if stream_reader is None:
            # This will happen if we try to get a StreamReader for a stream that no
            # longer exists, for example if a user clicks to expand a stream the very
            # instant before it's deleted from the server. We don't want to do anything
            return

        # Connect new signals
        stream_reader.frame_received.connect(self.frame_received)
        stream_reader.stream_state_changed.connect(self.state_changed)

        self.stream_reader = stream_reader

        # Don't wait for the first event to start displaying
        latest_frame = self.stream_reader.latest_processed_frame
        if latest_frame is not None:
            self.on_frame(latest_frame)
        else:
            self._on_state_change(stream_reader.status)

    @staticmethod
    def _get_stream_url(stream_conf: StreamConfiguration) -> Optional[str]:
        try:
            return api.get_stream_url(stream_conf.id)
        except (StreamConfigNotFoundError, StreamNotOpenedError):
            return None
