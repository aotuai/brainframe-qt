import logging
import typing
from threading import RLock, Thread
from typing import Set

from brainframe.api import StatusReceiver
from time import sleep

from brainframe.shared.gstreamer.stream_reader import GstStreamReader
from brainframe.shared.stream_reader import StreamReader, StreamStatus
from brainframe.shared.utils import or_events
from .stream_listener import StreamListener
from .frame_syncer import FrameSyncer
from .zone_status_frame import ZoneStatusFrame


class SyncedStreamReader(StreamReader):
    """Reads frames from a stream and syncs them up with zone statuses."""

    def __init__(self,
                 stream_id: int,
                 stream_reader: GstStreamReader,
                 status_receiver: StatusReceiver):
        """Creates a new SyncedStreamReader.

        :param stream_id: The stream ID that this synced stream reader is for
        :param stream_reader: The stream reader to get frames from
        :param status_receiver: The StatusReceiver currently in use
        """
        self.stream_id = stream_id
        self._stream_reader = stream_reader
        self.status_receiver = status_receiver

        self.latest_processed_frame = typing.cast(ZoneStatusFrame, None)

        self.stream_listeners: Set[StreamListener] = set()
        self._stream_listeners_lock = RLock()

        # Start threads, now that the object is all set up
        self._thread = Thread(
            name=f"SyncedStreamReader thread for stream ID {stream_reader}",
            target=self._sync_detections_with_stream,
            daemon=False
        )
        self._thread.start()

    def alert_frame_listeners(self):
        with self._stream_listeners_lock:
            if self.status is StreamStatus.STREAMING:
                for listener in self.stream_listeners:
                    listener.frame_event.set()

    def alert_status_listeners(self, status: StreamStatus):
        """This should be called whenever the StreamStatus has changed"""
        with self._stream_listeners_lock:
            if status is StreamStatus.INITIALIZING:
                for listener in self.stream_listeners:
                    listener.stream_initializing_event.set()
            elif status is StreamStatus.HALTED:
                for listener in self.stream_listeners:
                    listener.stream_halted_event.set()
            elif status is StreamStatus.CLOSED:
                for listener in self.stream_listeners:
                    listener.stream_closed_event.set()
            else:
                logging.critical("SyncedStreamReader: An event was called, but"
                                 " was not actually necessary!")
                for listener in self.stream_listeners:
                    listener.stream_error_event.set()

    def add_listener(self, listener: StreamListener):
        with self._stream_listeners_lock:
            self.stream_listeners.add(listener)
            if self.status is not StreamStatus.STREAMING:
                self.alert_status_listeners(self.status)
            elif self.latest_processed_frame is not None:
                self.alert_frame_listeners()
            else:
                listener.stream_initializing_event.set()

    def remove_listener(self, listener: StreamListener):
        with self._stream_listeners_lock:
            self.stream_listeners.remove(listener)
            listener.clear_all_events()

    @property
    def status(self) -> StreamStatus:
        return self._stream_reader.status

    @property
    def latest_frame(self):
        return self._stream_reader.latest_frame

    @property
    def new_frame_event(self):
        return self._stream_reader.new_frame_event

    @property
    def new_status_event(self):
        return self._stream_reader.new_status_event

    def set_runtime_option_vals(self, runtime_options: dict):
        self._stream_reader.set_runtime_option_vals(runtime_options)

    def _sync_detections_with_stream(self):
        while self.status != StreamStatus.INITIALIZING:
            sleep(0.01)

        # Create the FrameSyncer
        frame_syncer = FrameSyncer()

        frame_or_status_event = or_events(self._stream_reader.new_frame_event,
                                          self._stream_reader.new_status_event)

        while True:
            frame_or_status_event.wait()

            if self._stream_reader.new_status_event.is_set():
                self._stream_reader.new_status_event.clear()
                if self.status is StreamStatus.CLOSED:
                    break
                if self.status is not StreamStatus.STREAMING:
                    self.alert_status_listeners(self.status)
                    continue

            # If streaming is the new event we need to process the frame
            if not self._stream_reader.new_frame_event.is_set():
                continue

            # new_frame_event must have been triggered
            self._stream_reader.new_frame_event.clear()

            # Get the new frame + timestamp
            frame_tstamp, frame_bgr = self._stream_reader.latest_frame
            frame_rgb = frame_bgr[..., ::-1].copy()
            del frame_bgr

            # Get the latest zone statuses from thread status receiver thread
            statuses = self.status_receiver.latest_statuses(self.stream_id)

            # Run the syncing algorithm
            new_processed_frame = frame_syncer.sync(
                frame_tstamp=frame_tstamp,
                frame=frame_rgb,
                zone_statuses=statuses
            )

            if new_processed_frame is not None:
                is_new = new_processed_frame != self.latest_processed_frame

                # This value must be set before alerting frame listeners. This
                # prevents a race condition where latest_processed_frame is
                # None
                self.latest_processed_frame = new_processed_frame

                # Alert frame listeners if this a new frame
                if is_new:
                    self.alert_frame_listeners()

        logging.info("SyncedStreamReader: Closing")

    def close(self):
        """Sends a request to close the SyncedStreamReader."""
        self._stream_reader.close()

    def wait_until_closed(self):
        """Hangs until the SyncedStreamReader has been closed."""
        self._stream_reader.wait_until_closed()
        self._thread.join()
