import logging
from enum import Enum, auto
from threading import Event
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal

from brainframe.api.bf_codecs import StreamConfiguration
from gstly import gobject_init
from gstly.abstract_stream_reader import StreamReader, StreamStatus
from gstly.gst_stream_reader import GstStreamReader

from brainframe_qt.api_utils import api
from brainframe_qt.util.events import or_events

from .frame_syncer import FrameSyncer
from .zone_status_frame import ZoneStatusFrame


class SyncedStatus(Enum):
    """SyncedStreamReader wrapper of gstly's StreamStatus.

    Adds PAUSED and FINISHED states.
    """
    INITIALIZING = auto()
    STREAMING = auto()
    HALTED = auto()
    CLOSED = auto()
    PAUSED = auto()
    """Streaming is paused client-side to save bandwidth/resources"""
    FINISHED = auto()
    """The SyncedStreamReader is terminating and its thread will close soon"""

    @classmethod
    def from_stream_status(cls, status: StreamStatus) -> "SyncedStatus":
        if status is StreamStatus.INITIALIZING:
            return cls.INITIALIZING
        elif status is StreamStatus.STREAMING:
            return cls.STREAMING
        elif status is StreamStatus.HALTED:
            return cls.HALTED
        elif status is StreamStatus.CLOSED:
            return cls.CLOSED
        else:
            raise ValueError(f"Unknown StreamStatus {status}")


class SyncedStreamReader(QObject):
    """Reads frames from a stream and syncs them up with zone statuses."""

    frame_received = pyqtSignal(ZoneStatusFrame)
    stream_state_changed = pyqtSignal(SyncedStatus)

    finished = pyqtSignal()

    REHOSTED_VIDEO_TYPES = [
        StreamConfiguration.ConnType.WEBCAM,
        StreamConfiguration.ConnType.FILE,
    ]
    """Video types that are re-hosted by the server"""

    def __init__(
        self,
        stream_conf: StreamConfiguration,
        stream_url: str,
        *,
        parent: QObject
    ):
        """Creates a new SyncedStreamReader.

        :param stream_conf: The stream that this synced stream reader is for
        :param stream_url: The url of the stream
        """
        super().__init__(parent=parent)

        self.stream_conf = stream_conf
        self.stream_url = stream_url

        self._stream_reader: Optional[GstStreamReader] = None

        self.latest_processed_frame: Optional[ZoneStatusFrame] = None
        """Latest frame synced with results. None if no frames have been synced yet"""

        self.frame_syncer = FrameSyncer()

        self._stream_status = SyncedStatus.FINISHED

        self._start_streaming_event = Event()
        """Used to request the thread to start streaming"""
        self._pause_streaming_event = Event()
        """Used to request the thread to (temporarily) pause streaming"""

        self._start_streaming_event.set()

    @property
    def is_streaming_paused(self) -> bool:
        """Whether the stream is paused or has been requested to do so"""
        return (
            self._pause_streaming_event.is_set()
            or self.stream_status is SyncedStatus.PAUSED
        )

    @property
    def stream_status(self) -> SyncedStatus:
        """The current status of the stream"""
        return self._stream_status

    @stream_status.setter
    def stream_status(self, stream_status: SyncedStatus) -> None:
        """[private] Setter method for the stream status

        The stream_state_changed signal is emitted if the status changes.
        """
        if stream_status is not self._stream_status:
            self._stream_status = stream_status
            self.stream_state_changed.emit(stream_status)

    def close(self) -> None:
        """Sends a request to close the SyncedStreamReader"""
        logging.info(f"SyncedStreamReader for stream {self.stream_conf.id} closing")

        self.thread().quit()
        self.thread().requestInterruption()

    def pause_streaming(self) -> None:
        """Pause streaming.

        Streaming is not immediately paused, but will be handled in the main loop in
        _process_stream_events
        """
        self._pause_streaming_event.set()

    def resume_streaming(self) -> None:
        """Resume (more accurately, re-start) streaming.

        Streaming is not immediately paused, but will be handled in the main loop. This
        function does nothing (except print a warning) if the stream is not already
        paused.
        """
        if not self.is_streaming_paused:
            logging.warning(
                "Attempted to unpause streaming on SyncedStreamReader for stream "
                f"{self.stream_conf.id}, but it is not paused."
            )
            return

        self._start_streaming_event.set()

    def run(self) -> None:
        """Main loop for the created thread"""
        while not self.thread().isInterruptionRequested():
            if self._start_streaming_event.wait(0.2):
                self._start_streaming()
                self._process_stream_events()

        if self._stream_reader is not None:
            self._stop_streaming()

        self._finish()

    def wait_until_closed(self) -> None:
        """Hangs until the SyncedStreamReader has been closed. Must be called from
        another QThread"""
        if self._stream_reader is not None:
            self._stream_reader.wait_until_closed()

        self.thread().wait()

    def _finish(self) -> None:
        """Final clean-up for the SyncedStreamReader.

        To be called during complete stream shutdown, not simple pauses.
        Sets the status to FINISHED and emits the `finished` signal
        """
        logging.info(f"SyncedStreamReader for stream {self.stream_conf.id} closed")

        self.stream_status = SyncedStatus.FINISHED
        self.finished.emit()

    def _handle_frame_event(self) -> None:
        self._stream_reader.new_frame_event.clear()

        # Get the new frame + timestamp
        frame_tstamp, frame_bgr = self._stream_reader.latest_frame
        frame_rgb = frame_bgr[..., ::-1].copy()
        del frame_bgr

        # Get the latest zone statuses from status receiver thread
        statuses = api.get_status_receiver().latest_statuses(self.stream_conf.id)

        # Run the syncing algorithm
        new_processed_frame = self.frame_syncer.sync(
            latest_frame=ZoneStatusFrame(
                frame=frame_rgb,
                tstamp=frame_tstamp,
            ),
            latest_zone_statuses=statuses
        )

        if new_processed_frame is not None:
            if self.latest_processed_frame is None:
                is_new = True
            else:
                previous_tstamp = self.latest_processed_frame.tstamp
                new_tstamp = new_processed_frame.tstamp
                is_new = new_tstamp > previous_tstamp

            # This value must be set before alerting frame listeners. This prevents a
            # race condition where latest_processed_frame is None
            self.latest_processed_frame = new_processed_frame

            # Alert frame listeners if this a new frame
            if is_new:
                self.frame_received.emit(self.latest_processed_frame)

    def _handle_status_event(self) -> None:
        self._stream_reader.new_status_event.clear()

        self.stream_status = SyncedStatus.from_stream_status(self._stream_reader.status)

    def _start_streaming(self) -> None:
        """Create a new GstStreamReader. Gstreamer streaming begins immediately"""
        self._start_streaming_event.clear()

        pipeline: Optional[str] = self.stream_conf.connection_options.get("pipeline")

        latency = StreamReader.DEFAULT_LATENCY
        if self.stream_conf.connection_type in self.REHOSTED_VIDEO_TYPES:
            latency = StreamReader.REHOSTED_LATENCY

        # Streams created with a premises are always proxied from that premises
        is_proxied = self.stream_conf.premises_id is not None

        gobject_init.start()

        self._stream_reader = GstStreamReader(
            url=self.stream_url,
            latency=latency,
            runtime_options=self.stream_conf.runtime_options,
            pipeline_str=pipeline,
            proxied=is_proxied
        )

    def _stop_streaming(self) -> None:
        """Stop the current stream. Blocking function.

        Tells the GstStreamReader to close and wait for the thread to join. Then
        discards the reference to the GstStreamReader
        """
        self._stream_reader.wait_until_closed()
        self._stream_reader = None

    def _process_stream_events(self) -> None:
        """Handle posted events in current object and within the GstStreamReader"""
        if self._stream_reader is None:
            logging.warning(
                f"Attempted to process stream events on SyncedStreamReader for stream "
                f"{self.stream_conf.id} without a GstStreamReader set"
            )
            return

        frame_or_status_event = or_events(self._stream_reader.new_frame_event,
                                          self._stream_reader.new_status_event)

        while not self.thread().isInterruptionRequested():

            if self._pause_streaming_event.is_set():
                # Streaming paused. Stop loop for now
                self.stream_status = SyncedStatus.PAUSED
                self._pause_streaming_event.clear()
                break

            if not frame_or_status_event.wait(0.2):
                continue

            if self._stream_reader.new_status_event.is_set():
                self._handle_status_event()
            if self._stream_reader.new_frame_event.is_set():
                self._handle_frame_event()

        if self._stream_reader is not None:
            self._stop_streaming()
