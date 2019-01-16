import logging
from uuid import UUID
from typing import List
from threading import Thread
from typing import Optional, Dict

import cv2
import numpy as np

from brainframe.client.api.status_poller import StatusPoller
from brainframe.client.api.codecs import ZoneStatus
from brainframe.shared.stream_reader import StreamReader, StreamStatus
from brainframe.client.api.detection_tracks import DetectionTrack


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
        self.tracks: Dict[UUID, DetectionTrack] = {}

        self._latest_processed: ProcessedFrame = None

        self._thread = Thread(
            name=f"SyncedStreamReader thread for stream ID {stream_id}",
            target=self._sync_detections_with_stream)
        self._thread.start()

    @property
    def latest_processed_frame_rgb(self) -> ProcessedFrame:
        """Returns the latest frame with the most relevant available
        zone status information.

        :return: The processed frame
        """
        return self._latest_processed

    def _sync_detections_with_stream(self):
        # The last time we got inference
        last_inference_tstamp = -1

        buffer: List[ProcessedFrame] = []
        """Holds a list of empty ProcessedFrames until a new status comes in
        that is
                                      sB
        [Empty, Empty, Empty, Empty, Empty]
        Turn the first index Empty into a nice and full frame, put it into
        self._latest_processed
        """
        self.wait_until_initialized()

        last_used_zone_statuses = None

        while self.status != StreamStatus.CLOSED:
            # Wait for a new frame
            if not self.new_frame_event.wait(timeout=0.01):
                continue
            self.new_frame_event.clear()

            frame_tstamp, frame = self.latest_frame
            buffer.append(ProcessedFrame(frame, frame_tstamp, None, False))

            statuses = self.status_poller.latest_statuses(self.stream_id)

            # Get a timestamp from any of the zone statuses
            tstamp = statuses[-1].tstamp if len(statuses) else None

            # Check if this is a fresh zone_status or not
            if len(statuses) and last_inference_tstamp != tstamp:
                # Catch up to the previous inference frame
                while buffer[0].tstamp < last_inference_tstamp:
                    buffer.pop(0)
                last_inference_tstamp = tstamp

                # TODO: Iterate over all new detections, and add them to/create
                # DetectionTracks

            # If we have inference later than the current frame, update the
            # current frame
            if len(buffer) and buffer[0].tstamp <= last_inference_tstamp:
                frame = buffer.pop(0)
                rgb = cv2.cvtColor(frame.frame, cv2.COLOR_BGR2RGB)

                # TODO: Get a list of DetectionTracks that had a detection for
                # this timestamp
                self._latest_processed = ProcessedFrame(
                    frame=rgb,
                    tstamp=frame.tstamp,
                    zone_statuses=statuses,
                    has_new_statuses=statuses != last_used_zone_statuses)
                last_used_zone_statuses = statuses

            # Drain the buffer if it is getting too large
            while len(buffer) > self.MAX_BUF_SIZE:
                buffer.pop(0)

            # TODO: Prune DetectionTracks from self.track that haven't had a
            # detection in a while

        logging.info("SyncedStreamReader: Closing")
    def some_name(self):

    def close(self):
        """Sends a request to close the SyncedStreamReader."""
        super().close()

    def wait_until_closed(self):
        """Hangs until the SyncedStreamReader has been closed."""
        super().wait_until_closed()
        self._thread.join()


class StreamManager:
    """Keeps track of existing Stream objects, and creates new ones as
    necessary.
    """

    def __init__(self, status_poller: StatusPoller):
        self._stream_readers = {}
        self._status_poller = status_poller

    def start_streaming(self, stream_id: int,
                        url: str,
                        pipeline: Optional[str]) -> SyncedStreamReader:
        """Starts reading from the stream using the given information, or
        returns an existing reader if we're already reading this stream.

        :param stream_id: The unique ID of the stream
        :param url: The URL to stream on
        :param pipeline: A custom GStreamer pipeline, or None to use a default
            configuration
        :return: A Stream object
        """
        if stream_id not in self._stream_readers:
            stream_reader = SyncedStreamReader(
                stream_id=stream_id,
                url=url,
                pipeline=pipeline,
                status_poller=self._status_poller)
            self._stream_readers[stream_id] = stream_reader

        return self._stream_readers[stream_id]

    def close_stream(self, stream_id):
        """Close a specific stream and remove the reference.

        :param stream_id: The ID of the stream to delete
        """
        stream = self._close_stream_async(stream_id)
        stream.wait_until_closed()

    def close(self):
        """Close all streams and remove references"""
        closing_streams = []
        for stream_id in self._stream_readers.copy().keys():
            closing_streams.append(self._close_stream_async(stream_id))
        self._stream_readers = {}

        for stream in closing_streams:
            stream.wait_until_closed()

    def _close_stream_async(self, stream_id) -> SyncedStreamReader:
        stream = self._stream_readers.pop(stream_id)
        stream.close()
        return stream
