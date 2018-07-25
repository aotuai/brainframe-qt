import logging
from typing import List, Tuple, Union
from threading import Thread, RLock
from time import sleep, time

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
        :param stream_config: The StreamConfiguration for this stream
        :param status_poller: The StatusPoller currently in use
        """
        super().__init__(name="SyncedStreamReaderThread")
        self.url = url
        self.stream_id = stream_id
        self.status_poller = status_poller

        self._running = False
        self._cap = None
        self._latest = None
        self._stream_initialized = False

        self.start()

    @property
    def is_initialized(self):
        """Call this to check if the stream ever initialized. There is a
        startup period to even _starting_ to stream, and it is threaded.
        """
        return self._stream_initialized

    @property
    def is_running(self):
        """Once the stream HAS been initialized, you may want to check if it's
        even running still. Streams _can_ crash and sometimes be closed by the
        server, so keep an eye out if it's running. If the stream is no longer
        running, it WILL NOT TRY TO OPEN AGAIN.
        """
        return self._running

    @property
    def latest_processed_frame_rgb(self) -> Union[ProcessedFrame, None]:
        """Returns the processed frame, but in RGB instead of BGR."""
        latest = self._latest
        return latest

    def wait_until_initialized(self):
        """A convenience method to wait until the StreamReader has been
        initialized. Do not use if you don't intentionally want to block.
        """
        while not self._stream_initialized:
            if not self._running:
                break
            sleep(.001)  # To prevent busy loops

    def run(self):
        self._running = True

        with type(self).video_capture_lock:
            self._cap = cv2.VideoCapture(self.url)

        # Get the first frame to prove the stream is up. If not, end the stream.
        _, first_frame = self._cap.read()
        if first_frame is None:
            logging.info("StreamReader: Unable to get first frame from stream."
                         " Closing.")
            self._running = False
            return
        self._stream_initialized = True

        # The last time we got inference
        last_inference_tstamp = -1

        frame_buf = []

        while self._running:
            # Get a frame and buffer it
            _, frame = self._cap.read()
            tstamp = time()
            if frame is None:
                logging.info("SyncedStreamReader: No more frames in stream.")
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
                self._latest = ProcessedFrame(
                    rgb,
                    frame.tstamp,
                    zone_statuses)

            # Drain the buffer if it is getting too large
            while len(frame_buf) > self.MAX_BUF_SIZE:
                frame_buf.pop(0)

        logging.info("SyncedStreamReader: Closing")
        self._running = False

    def close(self):
        self._running = False
        self.join()
        if self._cap is not None:
            self._cap.release()


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

        if not self._stream_readers[url].is_running:
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
