import logging
from threading import Event
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from brainframe.api.bf_codecs import StreamConfiguration
from brainframe.api.bf_errors import StreamConfigNotFoundError, StreamNotOpenedError

from brainframe_qt.api_utils import api, get_stream_manager
from brainframe_qt.api_utils.streaming import SyncedStreamReader
from brainframe_qt.api_utils.streaming.synced_reader import SyncedStatus
from brainframe_qt.api_utils.streaming.zone_status_frame import ZoneStatusFrame
from brainframe_qt.ui.resources import QTAsyncWorker


class StreamEventManager(QObject):

    stream_initializing = pyqtSignal()
    stream_halted = pyqtSignal()
    stream_closed = pyqtSignal()
    stream_paused = pyqtSignal()
    stream_finished = pyqtSignal()

    stream_error = pyqtSignal()

    frame_received = pyqtSignal(ZoneStatusFrame)

    VIDEO_FRAME_RATE = 30
    """Frame rate of polling loop in FPS"""

    def __init__(self, *, parent: QObject):
        """Manages events from the stream's SyncedStreamReader"""
        super().__init__(parent=parent)

        self._frame_event = Event()
        self._status_event = Event()

        self.stream_conf: Optional[StreamConfiguration] = None
        self.stream_reader: Optional[SyncedStreamReader] = None

        self._event_timer = self._init_event_timer()

        self._init_signals()

    def _init_event_timer(self) -> QTimer:
        timer = QTimer(parent=self)

        timer.setInterval(1000 // self.VIDEO_FRAME_RATE)
        timer.start()

        return timer

    def _init_signals(self) -> None:
        self._event_timer.timeout.connect(self._process_events)

    @property
    def is_streaming_paused(self) -> bool:
        if self.stream_conf is None:
            return False
        if self.stream_reader is None:
            return False

        return self.stream_reader.is_streaming_paused

    def change_stream(self, stream_conf: StreamConfiguration) -> None:
        if self.stream_reader is not None:
            self.stop_streaming()

        self.stream_conf = stream_conf
        self.start_streaming()

    def pause_streaming(self) -> None:
        if self.stream_reader is None:
            logging.warning(
                f"Attempted to pause StreamEventManager, but it had no "
                f"SyncedStreamReader"
            )
            return

        self.stream_reader.pause_streaming()

    def resume_streaming(self) -> None:
        if self.stream_reader is None:
            logging.warning(
                f"Attempted to resume StreamEventManager, but it had no "
                f"SyncedStreamReader"
            )
            return

        if self.stream_reader.stream_status is not SyncedStatus.PAUSED:
            logging.warning(
                f"Attempted to resume StreamEventManager streaming for stream "
                f"{self.stream_conf.id}, but it was not paused"
            )
            return

        self.stream_reader.resume_streaming()

    def start_streaming(self) -> None:

        # Store the current stream_conf before async code is run to check to see if we
        # should abort after async
        stream_conf = self.stream_conf

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

    def stop_streaming(self) -> None:
        if self.stream_reader is None:
            logging.warning(
                f"Attempted to stop StreamEventManager, but it had no "
                f"SyncedStreamReader"
            )
            return

        self._unsubscribe_from_stream()

        self.stream_conf = None

    def _handle_frame_signal(self, _frame: ZoneStatusFrame) -> None:
        """Connected to the SyncedStreamReader"""
        self._frame_event.set()

    def _handle_status_signal(self) -> None:
        self._status_event.set()

    def _on_frame(self):
        self._frame_event.clear()

        if self.stream_reader is None:
            logging.info(
                f"StreamEventManager for stream {self.stream_conf.id} received "
                f"frame event, but SyncedStreamReader is None")
            return

        frame = self.stream_reader.latest_processed_frame

        if frame is None:
            logging.info(
                f"StreamEventManager for stream {self.stream_conf.id} received "
                f"frame event, but frame is None")
            return

        self.frame_received.emit(frame)

    def _on_state_change(self) -> None:
        self._status_event.clear()

        if self.stream_reader is None:
            logging.info(
                f"StreamEventManager for stream {self.stream_conf.id} received "
                f"status event, but SyncedStreamReader is None")
            return

        state = self.stream_reader.stream_status

        if state is SyncedStatus.INITIALIZING:
            self.stream_initializing.emit()
        elif state is SyncedStatus.HALTED:
            self.stream_halted.emit()
        elif state is SyncedStatus.CLOSED:
            self.stream_closed.emit()
        elif state is SyncedStatus.PAUSED:
            self.stream_paused.emit()
        elif state is SyncedStatus.FINISHED:
            self.stream_finished.emit()
        elif state is SyncedStatus.STREAMING:
            # Streaming, but no frame received yet
            self.stream_initializing.emit()
        else:
            self.stream_error.emit()

    def _process_events(self) -> None:
        if self._frame_event.is_set():
            self._on_frame()
        if self._status_event.is_set():
            self._on_state_change()

    def _unsubscribe_from_stream(self) -> None:
        """Remove the StreamEventManager's reference to the SyncedStreamReader after
        disconnecting the connected signals/slots.

        Note that this does not directly delete/remove/stop the SyncedStreamReader. We
        rely on garbage collection to do this. Multiple StreamWidgets (each with their
        own StreamEventManager) could be using the same SyncedStreamReader.
        """
        if self.stream_reader is None:
            logging.warning(
                "Attempted to unsubscribe StreamEventManager from stream when it was "
                "already disconnected"
            )
            return

        self.stream_reader.frame_received.disconnect(self._handle_frame_signal)
        self.stream_reader.stream_state_changed.disconnect(self._handle_status_signal)

        self._frame_event.clear()
        self._status_event.clear()

        self.stream_reader = None

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
        stream_reader.frame_received.connect(self._handle_frame_signal)
        stream_reader.stream_state_changed.connect(self._handle_status_signal)

        self.stream_reader = stream_reader

        # Don't wait for the first event to start displaying
        latest_frame = self.stream_reader.latest_processed_frame
        if latest_frame is not None:
            self._on_frame()
        else:
            self._on_state_change()

    @staticmethod
    def _get_stream_url(stream_conf: StreamConfiguration) -> Optional[str]:
        try:
            return api.get_stream_url(stream_conf.id)
        except (StreamConfigNotFoundError, StreamNotOpenedError):
            return None
