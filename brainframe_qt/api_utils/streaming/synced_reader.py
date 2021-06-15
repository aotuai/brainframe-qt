import logging
from threading import Thread, Event
from time import sleep
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal

from gstly.abstract_stream_reader import StreamReader, StreamStatus, FRAME
from gstly.gst_stream_reader import GstStreamReader

from brainframe_qt.api_utils import api
from brainframe_qt.ui.resources.mixins.base_mixin import ABCObject
from brainframe_qt.util.events import or_events

from .frame_syncer import FrameSyncer
from .zone_status_frame import ZoneStatusFrame


class SyncedStreamReader(StreamReader, QObject, metaclass=ABCObject):
    """Reads frames from a stream and syncs them up with zone statuses."""

    frame_received = pyqtSignal(ZoneStatusFrame)
    stream_state_changed = pyqtSignal(StreamStatus)

    def __init__(
        self,
        stream_id: int,
        stream_reader: GstStreamReader,
        *,
        parent: QObject
    ):
        """Creates a new SyncedStreamReader.

        :param stream_id: The stream ID that this synced stream reader is for
        :param stream_reader: The stream reader to get frames from
        """
        super().__init__(parent=parent)

        self.stream_id = stream_id
        self._stream_reader = stream_reader

        self.latest_processed_frame: Optional[ZoneStatusFrame] = None
        """Latest frame synced with results. None if no frames have been synced yet"""

        self.frame_syncer = FrameSyncer()

        # Start threads, now that the object is all set up
        self._thread = Thread(
            name=f"SyncedStreamReader thread for stream ID {stream_reader}",
            target=self._sync_detections_with_stream,
            daemon=True
        )
        self._thread.start()

    @property
    def status(self) -> StreamStatus:
        return self._stream_reader.status

    @property
    def latest_frame(self) -> FRAME:
        return self._stream_reader.latest_frame

    @property
    def new_frame_event(self) -> Event:
        return self._stream_reader.new_frame_event

    @property
    def new_status_event(self) -> Event:
        return self._stream_reader.new_status_event

    def set_runtime_option_vals(self, runtime_options: dict) -> None:
        self._stream_reader.set_runtime_option_vals(runtime_options)

    def _sync_detections_with_stream(self) -> None:
        while self.status is not StreamStatus.INITIALIZING:
            sleep(0.01)

        frame_or_status_event = or_events(self._stream_reader.new_frame_event,
                                          self._stream_reader.new_status_event)

        while self.status is not StreamStatus.CLOSED:
            frame_or_status_event.wait()

            if self._stream_reader.new_status_event.is_set():
                self._handle_status_event()
            if self._stream_reader.new_frame_event.is_set():
                self._handle_frame_event()

        logging.info("SyncedStreamReader: Closing")

    def _handle_status_event(self) -> None:
        self._stream_reader.new_status_event.clear()
        self.stream_state_changed.emit(self.status)

    def _handle_frame_event(self) -> None:
        self._stream_reader.new_frame_event.clear()

        # Get the new frame + timestamp
        frame_tstamp, frame_bgr = self._stream_reader.latest_frame
        frame_rgb = frame_bgr[..., ::-1].copy()
        del frame_bgr

        # Get the latest zone statuses from status receiver thread
        statuses = api.get_status_receiver().latest_statuses(self.stream_id)

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

    def close(self) -> None:
        """Sends a request to close the SyncedStreamReader."""
        self._stream_reader.close()

    def wait_until_closed(self) -> None:
        """Hangs until the SyncedStreamReader has been closed."""
        self._stream_reader.wait_until_closed()
        self._thread.join()
