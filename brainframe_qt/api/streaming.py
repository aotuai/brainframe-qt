import logging
from threading import Thread

import cv2

from brainframe.client.api.codecs import StreamConfiguration
from brainframe.client.api.status_poller import StatusPoller
from brainframe.shared.stream_utils import StreamReader, StreamStatus


class ProcessedFrame:
    """A frame that may or may not have undergone processing on the server."""

    def __init__(self, frame, tstamp, zone_statuses):
        self.frame = frame
        self.tstamp = tstamp
        self.zone_statuses = zone_statuses


class SyncedStreamReader(StreamReader):
    """Reads frames from a stream and syncs them up with zone statuses."""

    MAX_BUF_SIZE = 100

    def __init__(self,
                 url: str,
                 stream_id: int,
                 status_poller: StatusPoller):
        """Creates a new SyncedStreamReader.

        :param url: The URL of the stream to read from
        :param stream_id: The ID of the stream to read from
        :param status_poller: The StatusPoller currently in use
        """
        super().__init__(url)
        self.url = url
        self.stream_id = stream_id
        self.status_poller = status_poller

        self._latest_processed = None

        self._thread = Thread(
            name=f"SyncedStreamReader thread for stream ID {stream_id}",
            target=self._sync_detections_with_stream)
        self._thread.start()

    @property
    def latest_processed_frame_rgb(self):
        return self._latest_processed

    def _sync_detections_with_stream(self):
        # The last time we got inference
        last_inference_tstamp = -1

        frame_buf = []

        self.wait_until_initialized()

        while self.status != StreamStatus.CLOSED:
            # Wait for a new frame
            if not self.new_frame_event.wait(timeout=0.01):
                continue
            self.new_frame_event.clear()

            frame_tstamp, frame = self.latest_frame
            frame_buf.append(ProcessedFrame(frame, frame_tstamp, None))

            zone_statuses = self.status_poller.latest_statuses(self.stream_id)

            tstamp = zone_statuses[-1].tstamp if zone_statuses else None

            # Check if this is a fresh zone_status or not
            if zone_statuses and last_inference_tstamp != tstamp:
                # Catch up to the previous inference frame
                while frame_buf[0].tstamp < last_inference_tstamp:
                    frame_buf.pop(0)

                last_inference_tstamp = tstamp

            # If we have inference later than the current frame, update the
            # current frame
            if frame_buf and frame_buf[0].tstamp <= last_inference_tstamp:
                frame = frame_buf.pop(0)
                rgb = cv2.cvtColor(frame.frame, cv2.COLOR_BGR2RGB)
                self._latest_processed = ProcessedFrame(
                    rgb, frame.tstamp, zone_statuses)

            # Drain the buffer if it is getting too large
            while len(frame_buf) > self.MAX_BUF_SIZE:
                frame_buf.pop(0)

        logging.info("SyncedStreamReader: Closing")

    def close(self):
        super().close()
        self._thread.join()


class StreamManager:
    """Keeps track of existing Stream objects, and creates new ones as
    necessary.
    """

    def __init__(self, status_poller: StatusPoller):
        self._stream_readers = {}
        self._status_poller = status_poller

    def get_stream(self, url: str, stream_config: StreamConfiguration) \
            -> SyncedStreamReader:
        """Gets a specific stream object OR creates the connection and returns
        it if it does not already exist

        :param url: The URL of the stream to connect to
        :param stream_config: The StreamConfiguration for this stream
        :return: A Stream object
        """

        if url not in self._stream_readers:
            stream_reader = SyncedStreamReader(
                url, stream_config.id, self._status_poller)
            self._stream_readers[url] = stream_reader
            return stream_reader

        if self._stream_readers[url].status is StreamStatus.HALTED:
            # Stream not running. Starting a new one.
            self._stream_readers[url].close()
            stream_reader = SyncedStreamReader(
                url, stream_config.id, self._status_poller)
            return stream_reader

        return self._stream_readers[url]

    def close_stream_by_url(self, url):
        """Close a specific stream and remove the reference.

        :param url: The URL of the stream to delete
        """
        self._stream_readers[url].close()
        del self._stream_readers[url]

    def close_stream_by_id(self, stream_id):
        """Close a specific stream and remove the reference.

        :param stream_id: The ID of the stream to delete
        """
        for url, stream_reader in self._stream_readers.items():
            if stream_reader.stream_id == stream_id:
                self.close_stream_by_url(url)
                break

    def close(self):
        """Close all streams and remove references"""
        for url in self._stream_readers.copy().keys():
            self.close_stream_by_url(url)
        self._stream_readers = {}
