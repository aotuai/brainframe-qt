import logging
import typing
from threading import Event, RLock
from time import sleep
from typing import Dict, Generator, List, Optional, Set, Tuple
from uuid import UUID, uuid4

import numpy as np
from brainframe.api import StatusReceiver
from brainframe.api.bf_codecs import ZoneStatus

from brainframe.client.api_utils.detection_tracks import DetectionTrack
from brainframe.shared.constants import DEFAULT_ZONE_NAME
from brainframe.shared.gstreamer.stream_reader import GstStreamReader
from brainframe.shared.stream_reader import StreamReader, StreamStatus
from brainframe.shared.utils import or_events
from brainframe.shared.exiting import ServiceThread
from .frame_buffer import SyncedFrameBuffer
from .zone_status_frame import ZoneStatusFrame


class StreamListener:
    """This is used by SyncedStreamReader to pass events to the UI"""

    def __init__(self):
        self.frame_event = Event()
        """Called when a new ProcessedFrame is ready"""

        self.stream_initializing_event = Event()
        """Called when the stream starts initializing"""

        self.stream_halted_event = Event()
        """Called when the stream has halted"""

        self.stream_closed_event = Event()
        """Called when the stream connection has closed"""

        self.stream_error_event = Event()
        """Called upon serious error (this shouldn't happen?)"""

    def clear_all_events(self):
        self.frame_event.clear()
        self.stream_initializing_event.clear()
        self.stream_halted_event.clear()
        self.stream_closed_event.clear()
        self.stream_error_event.clear()


class SyncedStreamReader(StreamReader):
    """Reads frames from a stream and syncs them up with zone statuses."""
    MAX_CACHE_TRACK_SECONDS = 30

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
        self._thread = ServiceThread(
            name=f"SyncedStreamReader thread for stream ID {stream_reader}",
            target=self._sync_detections_with_stream)
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

        # Create the frame syncing generator and initialize it
        frame_syncer = self.sync_frames()
        next(frame_syncer)

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
            frame_tstamp, frame = self._stream_reader.latest_frame

            # Get the latest zone statuses from thread status receiver thread
            statuses = self.status_receiver.latest_statuses(self.stream_id)

            # Run the syncing algorithm
            new_processed_frame = frame_syncer.send(
                (frame_tstamp, frame, statuses))

            if new_processed_frame is not None:
                is_new = new_processed_frame != self.latest_processed_frame

                # This value must be set before alerting frame listeners
                # this prevents a race condition where latest_processed_frame
                #  is None
                self.latest_processed_frame = new_processed_frame

                # Alert frame listeners if this a new frame
                if is_new:
                    self.alert_frame_listeners()

        logging.info("SyncedStreamReader: Closing")

    def sync_frames(self) -> Generator[ZoneStatusFrame,
                                       Tuple[float,
                                             np.ndarray,
                                             Dict[str, ZoneStatus]],
                                       None]:
        """A generator where the input is frame_tstamp, frame, statuses and
        it yields out ProcessedFrames where the zonestatus and frames are
        synced up. """

        last_status_tstamp: float = -1
        """Keep track of the timestamp of the last new zonestatus that was 
        received."""

        last_used_zone_statuses: Optional[Dict[str, ZoneStatus]] = None
        """The last zone status object that was put into a processed frame.
        Useful for identifying if a ProcessFrame has new information, or is 
        simply paired with old information."""

        latest_processed = None
        """Keeps track of the latest ProcessedFrame with information"""

        buffer = SyncedFrameBuffer()
        """Holds a queue of empty ProcessedFrames until a new status comes in
        that is
                                      sB
        [empty, empty, empty, empty, empty]
        Turn the first index Empty into a nice and full frame, put it into
        self._latest_processed
        """

        tracks: Dict[UUID, DetectionTrack] = {}
        """Keep a dict of Detection.track_id: DetectionTrack of all detections
        that are ongoing. Then, every once in a while, prune DetectionTracks 
        that haven't gotten updates in a while."""

        # Type-hint the input to the generator
        # noinspection PyUnusedLocal
        statuses: Dict[str, ZoneStatus]

        while True:
            frame_tstamp, frame, statuses = yield latest_processed

            buffer.add_frame(
                ZoneStatusFrame(
                    frame=frame,
                    tstamp=frame_tstamp,
                    zone_statuses=None,
                    has_new_statuses=False,
                    tracks=None
                )
            )

            # Analysis still spinning up. Skip
            if not len(statuses):
                latest_processed = None
                continue

            # Get timestamp off of default zone's status (all should be equal)
            status_tstamp = statuses[DEFAULT_ZONE_NAME].tstamp

            # Check if this is a fresh zone_status or not
            if last_status_tstamp != status_tstamp:
                # Catch buffer up to the previous inference frame (get rid of
                # frames that the client will never render because it's running
                # too far behind)
                buffer.pop_until(last_status_tstamp)

                last_status_tstamp = status_tstamp

                # Iterate over all new detections, and add them to their tracks
                dets = statuses[DEFAULT_ZONE_NAME].within
                for det in dets:
                    # Create new tracks where necessary
                    track_id = det.track_id if det.track_id else uuid4()

                    if det.track_id not in tracks:
                        tracks[track_id] = DetectionTrack()
                    tracks[track_id].add_detection(det, status_tstamp)

            # If we have a zone status/inference result newer than the latest
            # received frame, associate the buffer's oldest frame with the zone
            # status
            popped_frame = buffer.pop_if_older(last_status_tstamp)

            # Pop a frame if we're over the combined buffer max, but we
            # also have more frames than the guaranteed minimum
            if popped_frame is None:
                if buffer.is_full and not buffer.needs_guaranteed_space:
                    popped_frame = buffer.pop_oldest()

            # If we have a frame using any means, use it
            if popped_frame is not None:
                latest_processed = self._apply_statuses_to_frame(
                    frame=popped_frame,
                    statuses=statuses,
                    tracks=tracks,
                    has_new_statuses=last_used_zone_statuses != statuses
                )

                last_used_zone_statuses = statuses

            # Prune DetectionTracks that haven't had a detection in a while
            for uuid, track in list(tracks.items()):
                detection_lapse = frame_tstamp - track.latest_tstamp
                if detection_lapse > self.MAX_CACHE_TRACK_SECONDS:
                    del tracks[uuid]

    def close(self):
        """Sends a request to close the SyncedStreamReader."""
        self._stream_reader.close()

    def wait_until_closed(self):
        """Hangs until the SyncedStreamReader has been closed."""
        self._stream_reader.wait_until_closed()
        self._thread.join()

    # noinspection PyMethodMayBeStatic
    def _apply_statuses_to_frame(self, frame: ZoneStatusFrame,
                                 statuses: Dict[str, ZoneStatus],
                                 tracks: Dict[UUID, DetectionTrack],
                                 has_new_statuses: bool) \
            -> ZoneStatusFrame:

        # Get timestamp off of default zone's status (all should be equal)
        status_tstamp = statuses[DEFAULT_ZONE_NAME].tstamp

        # Get a list of DetectionTracks that had a detection for
        # this timestamp
        relevant_dets = [dt.copy() for dt in tracks.values()
                         if dt.latest_tstamp == status_tstamp]

        applied_frame = ZoneStatusFrame(
            frame=frame.frame_rgb,
            tstamp=frame.tstamp,
            zone_statuses=statuses,
            has_new_statuses=has_new_statuses,
            tracks=relevant_dets)

        return applied_frame
