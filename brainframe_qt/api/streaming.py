import logging
from threading import Thread, RLock
from time import sleep, time
from typing import Union
from enum import Enum

import cv2

from brainframe.client.api.codecs import StreamConfiguration
from brainframe.client.api.status_poller import StatusPoller


class ProcessedFrame:
    """A frame that may or may not have undergone processing on the server."""

    def __init__(self, frame, tstamp, zone_statuses):
        self.frame = frame
        self.tstamp = tstamp
        self.zone_statuses = zone_statuses


class SyncedStreamReader(Thread):
    """Reads frames from a stream and syncs them up with zone statuses."""

    class Status(Enum):
        INITIALIZING = "Initializing"
        """The stream is starting up, but isn't ready to stream yet."""
        STREAMING = "Streaming"
        """The stream is currently sending out frames."""
        HALTED = "Halted"
        """The source stopped providing frames, perhaps due to an error. The
        reader may start streaming in the future if possible.
        """
        CLOSED = "Closed"
        """The stream has been closed by a request. It will never stream again.
        """

    MAX_BUF_SIZE = 100

    video_capture_lock = RLock()
    """Lock that exists to solve a strange, occasional SIGSEGV in OpenCV when
    multiple threads attempt to create VideoCapture instances at the same time.
    
    It is not certain if this is the proper solution to the problem, but it does
    prevent it from happening
    """

    def __init__(self,
                 url: str,
                 stream_id: int,
                 status_poller: StatusPoller):
        """Creates a new SyncedStreamReader.

        :param url: The URL of the stream to read from
        :param stream_id: The ID of the stream to read from
        :param status_poller: The StatusPoller currently in use
        """
        super().__init__(name="SyncedStreamReaderThread")
        self.url = url
        self.stream_id = stream_id
        self.status_poller = status_poller

        self._cap = None
        self._latest = None
        self._status = SyncedStreamReader.Status.INITIALIZING

        self.start()

    @property
    def status(self)-> "SyncedStreamReader.Status":
        """Returns the current state of the SyncedStreamReader."""
        return self._status

    @property
    def latest_processed_frame_rgb(self) -> Union[ProcessedFrame, None]:
        """Returns the processed frame, but in RGB instead of BGR."""
        return self._latest

    def wait_until_initialized(self):
        """A convenience method to wait until the StreamReader has been
        initialized. Do not use if you don't intentionally want to block. This
        method will return even if the SyncedStreamReader failed during
        initialization, so it's not safe to assume that frames will be
        available.
        """
        while self._status == SyncedStreamReader.Status.INITIALIZING:
            sleep(.001)  # To prevent busy loops

    def run(self):
        self._status = SyncedStreamReader.Status.INITIALIZING

        with type(self).video_capture_lock:
            self._cap = cv2.VideoCapture(self.url)

        # Get the first frame to prove the stream is up. If not, end the stream.
        _, first_frame = self._cap.read()
        if first_frame is None:
            logging.warning("StreamReader: Unable to get first frame from "
                            "stream. Closing.")
            self._status = SyncedStreamReader.Status.HALTED
            return
        self._status = SyncedStreamReader.Status.STREAMING

        # The last time we got inference
        last_inference_tstamp = -1

        frame_buf = []

        while self._status == SyncedStreamReader.Status.STREAMING:
            # Get a frame and buffer it
            _, frame = self._cap.read()
            tstamp = time()
            if frame is None:
                logging.info("SyncedStreamReader: No more frames in stream.")
                self._status = SyncedStreamReader.Status.HALTED
                break
            frame_buf.append(ProcessedFrame(frame, tstamp, None))

            # Get the latest zone statuses and the timestamp
            zone_statuses = self.status_poller.latest_statuses(
                self.stream_id)

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
                self._latest = ProcessedFrame(rgb, frame.tstamp, zone_statuses)

            # Drain the buffer if it is getting too large
            while len(frame_buf) > self.MAX_BUF_SIZE:
                frame_buf.pop(0)

        logging.info("SyncedStreamReader: Closing")

    def close(self):
        self._status = SyncedStreamReader.Status.CLOSED
        self.join()
        if self._cap is not None:
            self._cap.release()


class StreamManager:
    """Keeps track of existing Stream objects, and creates new ones as
    necessary.
    """

    TRY_RESTARTING_DELAY = 5
    """Time in seconds between attempts to restart StreamReaders that have
    stopped running.
    """

    def __init__(self, status_poller: StatusPoller):
        self._stream_readers = {}
        self._status_poller = status_poller

        # Protects access to stream-related state
        self._lock = RLock()

        # Have a thread routinely attempt to restart halted stream readers
        self._restarter_running = False
        self._restarter_thread = Thread(
            name="RestartStreamReaders",
            target=self._restart_stream_readers)
        self._restarter_thread.start()

    def get_stream(self, url: str, stream_config: StreamConfiguration) \
            -> SyncedStreamReader:
        """Gets a specific stream object OR creates the connection and returns
        it if it does not already exist

        :param url: The URL of the stream to connect to
        :param stream_config: The StreamConfiguration for this stream
        :return: A Stream object
        """

        with self._lock:
            if url not in self._stream_readers:
                stream_reader = SyncedStreamReader(
                    url, stream_config.id, self._status_poller)
                self._stream_readers[url] = stream_reader
                return stream_reader

            if self._stream_readers[url].status == SyncedStreamReader.Status.HALTED:
                # Stream not running. Starting a new one.
                self._stream_readers[url].close()
                stream_reader = SyncedStreamReader(
                    url, stream_config.id, self._status_poller)
                return stream_reader

            return self._stream_readers[url]

    def close_stream(self, url):
        """Close a specific stream and remove the reference """
        self._stream_readers[url].close()
        del self._stream_readers[url]

    def close(self):
        """Close all streams and remove references"""
        for url in self._stream_readers.copy().keys():
            self.close_stream(url)
        self._stream_readers = {}

    def _restart_stream_readers(self):
        """Periodically tries to restart streams that have been halted."""
        self._restarter_running = True

        last_restart = time()

        while self._restarter_running:
            if time() - last_restart < self.TRY_RESTARTING_DELAY:
                sleep(0.001)
                continue

            with self._lock:
                for stream_id in self._stream_readers.keys():
                    if self._stream_readers[stream_id].status == \
                            SyncedStreamReader.Status.HALTED:
                        self._stream_readers[stream_id] = SyncedStreamReader(
                            self._stream_readers[stream_id].url,
                            self._stream_readers[stream_id].stream_id,
                            self._stream_readers[stream_id].status_poller)

            last_restart = time()
