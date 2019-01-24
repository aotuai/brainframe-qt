import logging
from threading import Thread, RLock
from typing import List, Optional, Generator, Tuple, Dict
from uuid import UUID, uuid4

import cv2
import numpy as np

from brainframe.client.api.codecs import ZoneStatus
from brainframe.client.api.detection_tracks import DetectionTrack
from brainframe.client.api.status_poller import StatusPoller
from brainframe.shared.constants import DEFAULT_ZONE_NAME
from brainframe.shared.stream_listener import StreamListener
from brainframe.shared.stream_reader import StreamReader, StreamStatus
from brainframe.shared.utils import or_events


class ProcessedFrame:
    """A frame that may or may not have undergone processing on the server."""

    def __init__(self, frame, tstamp, zone_statuses, has_new_statuses, tracks):
        """
        :param frame: RGB data on the frame
        :param tstamp: The timestamp of the frame
        :param zone_statuses: A zone status that is most relevant to this frame,
            though it might not be a result of this frame specifically
        :param has_new_statuses: True if this processed frame contains new
            zone statuses that have not appeared in previous processed frames
        """
        self.frame: np.ndarray = frame
        self.tstamp: float = tstamp
        self.zone_statuses: List[ZoneStatus] = zone_statuses
        self.has_new_zone_statuses = has_new_statuses
        self.tracks: List[DetectionTrack] = tracks


class SyncedStreamReader(StreamReader):
    """Reads frames from a stream and syncs them up with zone statuses."""
    MAX_BUF_SIZE = 100
    MAX_CACHE_TRACK_SECONDS = 30

    def __init__(self,
                 stream_id: int,
                 url: str,
                 pipeline: Optional[str],
                 status_poller: StatusPoller):
        """Creates a new SyncedStreamReader.

        :param stream_id: The unique Id of this stream
        :param url: The URL to connect to
        :pipeline: A custom GStreamer pipeline, or None to use a default
            configuration
        :param status_poller: The StatusPoller currently in use
        """
        super().__init__(url, pipeline)

        self.url = url
        self.pipeline = pipeline
        self.stream_id = stream_id
        self.status_poller = status_poller

        self.latest_processed_frame: ProcessedFrame = None

        self._thread = Thread(
            name=f"SyncedStreamReader thread for stream ID {stream_id}",
            target=self._sync_detections_with_stream)
        self._thread.start()

        self.stream_listeners = set()
        self._stream_listeners_lock = RLock()

    def alert_frame_listeners(self, processed_frame):

        with self._stream_listeners_lock:
            if self.status is StreamStatus.STREAMING:
                for listener in self.stream_listeners:
                    listener.signal_frame(processed_frame)

    def alert_status_listeners(self, status: StreamStatus):
        """This should be called whenever the StreamStatus has changed"""
        with self._stream_listeners_lock:
            if status is StreamStatus.INITIALIZING:
                for listener in self.stream_listeners:
                    listener.signal_stream_initializing()
            elif status is StreamStatus.HALTED:
                for listener in self.stream_listeners:
                    listener.signal_stream_halted()
            elif status is StreamStatus.CLOSED:
                for listener in self.stream_listeners:
                    listener.signal_stream_closed()
            else:
                logging.critical("SyncedStreamReader: An event was called, but"
                                 " was not actually necessary!")
                for listener in self.stream_listeners:
                    listener.signal_stream_error()

    def add_listener(self, listener: StreamListener):
        with self._stream_listeners_lock:
            self.stream_listeners.add(listener)
            if not self.status.STREAMING:
                self.alert_status_listeners(self.status)
            elif self.latest_processed_frame is not None:
                self.alert_frame_listeners(self.latest_processed_frame)
            else:
                self.alert_status_listeners(StreamStatus.INITIALIZING)

    def remove_listener(self, listener: StreamListener):
        with self._stream_listeners_lock:
            self.stream_listeners.remove(listener)

    def _sync_detections_with_stream(self):
        self.wait_until_initialized()

        # Create the frame syncing generator and initialize it
        frame_syncer = self.sync_frames()
        next(frame_syncer)

        frame_or_status_event = or_events(self.new_frame_event,
                                          self.new_status_event)

        while True:
            frame_or_status_event.wait()

            if self.new_status_event.is_set():
                self.new_status_event.clear()
                if self.status is StreamStatus.CLOSED:
                    break
                if self.status is not StreamStatus.STREAMING:
                    self.alert_status_listeners(self.status)
                    continue

            # If streaming is the new event we need to process the frame
            if not self.new_frame_event.is_set():
                continue

            # new_frame_event must have been triggered
            self.new_frame_event.clear()

            # Get the new frame + timestamp
            frame_tstamp, frame = self.latest_frame

            # Get the latest zone statuses from thread status poller thread
            statuses = self.status_poller.latest_statuses(self.stream_id)

            # Run the syncing algorithm
            new_processed_frame = frame_syncer.send(
                (frame_tstamp, frame, statuses))

            if new_processed_frame is not None:
                if new_processed_frame != self.latest_processed_frame:
                    self.alert_frame_listeners(new_processed_frame)
                self.latest_processed_frame = new_processed_frame

        logging.info("SyncedStreamReader: Closing")

    def sync_frames(self) -> Generator[ProcessedFrame,
                                       Tuple[float,
                                             np.ndarray,
                                             List[ZoneStatus]],
                                       None]:
        """A generator where the input is frame_tstamp, frame, statuses and
        it yields out ProcessedFrames where the zonestatus and frames are
        synced up. """

        last_status_tstamp = -1
        """Keep track of the timestamp of the last new zonestatus that was 
        received."""

        last_used_zone_statuses = None
        """The last zone statuse object that was put into a processed frame.
        Useful for identifying if a ProcessFrame has new information, or is 
        simply paired with old information."""

        latest_processed = None
        """Keeps track of the latest ProcessedFrame with information"""

        buffer: List[ProcessedFrame] = []
        """Holds a list of empty ProcessedFrames until a new status comes in
        that is
                                      sB
        [Empty, Empty, Empty, Empty, Empty]
        Turn the first index Empty into a nice and full frame, put it into
        self._latest_processed
        """

        tracks: Dict[UUID, DetectionTrack] = {}
        """Keep a dict of Detection.track_id: DetectionTrack of all detections
        that are ongoing. Then, every once in a while, prune DetectionTracks 
        that haven't gotten updates in a while."""

        # Type-hint the input to the generator
        # noinspection PyUnusedLocal
        statuses: List[ZoneStatus]

        while True:
            frame_tstamp, frame, statuses = yield latest_processed

            buffer.append(
                ProcessedFrame(frame, frame_tstamp, None, False, None))

            # Get a timestamp from any of the zone statuses
            status_tstamp = statuses[-1].tstamp if len(statuses) else None

            # Check if this is a fresh zone_status or not
            if len(statuses) and last_status_tstamp != status_tstamp:
                # Catch up to the previous inference frame
                while buffer[0].tstamp < last_status_tstamp:
                    buffer.pop(0)
                last_status_tstamp = status_tstamp

                # Iterate over all new detections, and add them to their tracks
                dets = next(s.detections for s in statuses
                            if s.zone.name == DEFAULT_ZONE_NAME)
                for det in dets:
                    # Create new tracks where necessary
                    track_id = det.track_id if det.track_id else uuid4()

                    if det.track_id not in tracks:
                        tracks[track_id] = DetectionTrack()
                    tracks[track_id].add_detection(det, status_tstamp)

            # If we have inference later than the current frame, update the
            # current frame
            if len(buffer) and buffer[0].tstamp <= last_status_tstamp:
                frame = buffer.pop(0)
                rgb = cv2.cvtColor(frame.frame, cv2.COLOR_BGR2RGB)

                # Get a list of DetectionTracks that had a detection for
                # this timestamp
                relevant_dets = [dt.copy() for dt in tracks.values()
                                 if dt.latest_tstamp == status_tstamp]

                latest_processed = ProcessedFrame(
                    frame=rgb,
                    tstamp=frame.tstamp,
                    zone_statuses=statuses,
                    has_new_statuses=statuses != last_used_zone_statuses,
                    tracks=relevant_dets)
                last_used_zone_statuses = statuses
            else:
                latest_processed = None

            # Drain the buffer if it is getting too large
            while len(buffer) > self.MAX_BUF_SIZE:
                buffer.pop(0)

            # Prune DetectionTracks that haven't had a detection in a while
            for uuid, track in list(tracks.items()):
                if frame_tstamp - track.latest_tstamp > self.MAX_CACHE_TRACK_SECONDS:
                    del tracks[uuid]

    def close(self):
        """Sends a request to close the SyncedStreamReader."""
        super().close()

    def wait_until_closed(self):
        """Hangs until the SyncedStreamReader has been closed."""
        super().wait_until_closed()
        self._thread.join()
