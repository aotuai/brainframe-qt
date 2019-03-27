from threading import RLock, Thread, Event
from time import time, sleep
import logging
from typing import Optional, Tuple

import cv2

from brainframe.shared.dependency_check import OpenCVDep
from brainframe.shared.stream_reader import (
    StreamReader,
    StreamReadError,
    StreamStatus,
    FRAME
)


class OpenCVStreamReader(StreamReader):
    """Reads from a stream and outputs frames with their respective timestamps.
    """

    TRY_RESTARTING_DELAY = 5
    """Time in seconds between attempts to restart StreamReaders that have
    stopped running.
    """

    video_capture_lock = RLock()
    """Lock that exists to solve a strange, occasional SIGSEGV in OpenCV when
    multiple threads attempt to create VideoCapture instances at the same time.

    It is not certain if this is the proper solution to the problem, but it
    does prevent it from happening
    """

    def __init__(self, url: str, *,
                 latency: int = StreamReader.DEFAULT_LATENCY,
                 pipeline: Optional[str] = None):
        """
        :param url: The URL to connect to
        :param latency: The latency to apply during streaming. A higher latency
            can lead to a smoother stream if the connection is unstable, but
            is generally unnecessary when the stream source is localized. If
            a custom pipeline is specified, this value will be ignored
        :param pipeline: A custom GStreamer pipeline, or None to use
            a default configuration
        """
        if not (OpenCVDep.gstreamer or OpenCVDep.ffmpeg):
            raise StreamReadError(
                "OpenCV is not built with GStreamer or FFmpeg")

        self.url = url
        self.pipeline = pipeline
        self.latency = latency

        self._cap = None
        self._status = StreamStatus.INITIALIZING
        self._latest_frame: FRAME = None

        self._new_frame_event = Event()
        self._new_status_event = Event()

        self._close_requested = False

        self._start_reading()

    @property
    def status(self) -> StreamStatus:
        """Returns the current state of the StreamReader."""
        return self._status

    @property
    def new_frame_event(self):
        return self._new_frame_event

    @property
    def new_status_event(self):
        return self._new_status_event

    @status.setter
    def status(self, status):
        if self._status is not status:
            self._status = status
            self.new_status_event.set()

    @property
    def latest_frame(self) -> FRAME:
        """Returns the (timestamp, frame) """
        latest = self._latest_frame
        return latest

    @property
    def latest_frame_rgb(self) -> FRAME:
        """Returns the frame, but in RGB instead of BGR"""
        timestamp, frame = self._latest_frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return timestamp, frame

    def close(self):
        """Sends a request to stop the StreamReader."""
        self._close_requested = True

    def wait_until_closed(self):
        """Hangs until the StreamReader is closed"""
        self._thread.join()

    def _wait_for_connection(self):
        last_frame_check = 0
        first_frame = None

        while self._cap is None or first_frame is None:
            if self._close_requested:
                return  # Abort early

            if time() - last_frame_check >= self.TRY_RESTARTING_DELAY:
                if self._close_requested:
                    return
                self._cap, first_frame = self._open_video_capture()

                if self._cap is None:
                    # We're having trouble connecting to the stream
                    self.status = StreamStatus.HALTED

                last_frame_check = time()

            sleep(0.001)

        # Get the first frame and get back to work
        self._latest_frame = first_frame
        self.status = StreamStatus.STREAMING

    def _read_from_stream(self):
        self.status = StreamStatus.INITIALIZING

        self._wait_for_connection()

        if self.status == StreamStatus.STREAMING:
            logging.info(f"Successfully started streaming {self.url}")
        else:
            logging.info(f"Stream did not start properly, status is "
                         f"{self.status}")

        while not self._close_requested:
            _, frame = self._cap.read()
            tstamp = time()

            if frame is None:
                self.status = StreamStatus.HALTED
                self._wait_for_connection()
            else:
                frame = (tstamp, frame)
                self._latest_frame = frame
                self._new_frame_event.set()

        # Mark the stream as closed if it stopped because of a close request
        logging.info("StreamReader: Closing")
        if self._cap is not None:
            self._cap.release()
        self.status = StreamStatus.CLOSED

        if not self._close_requested:
            logging.error("StreamReader: Thread closed unexpectedly!")

    def _start_reading(self):
        """Attempts to start the StreamReader."""
        self._thread = Thread(
            name=f"StreamReader thread for stream ID {self.url}",
            target=self._read_from_stream)
        self._thread.start()

    def _open_video_capture(self) -> \
            Tuple[Optional[cv2.VideoCapture], Optional[FRAME]]:
        """Attempts to open the capture.

        :return: The capture, (frame, timestamp) or None, None
         if the capture could not be opened
        """
        with self.video_capture_lock:
            if self._close_requested:
                return None, None

            if self.pipeline is not None:
                if not OpenCVDep.gstreamer:
                    raise StreamReadError(
                        "OpenCV was not compiled with GStreamer support so "
                        "custom pipelines are not usable")

                # Use the custom provided pipeline
                try:
                    pipeline = self.pipeline.format(url=self.url)
                except IndexError:
                    raise StreamReadError(
                        f"Invalid pipeline format: '{self.pipeline}'. "
                        "Pipelines must contain a '{url}' portion to be "
                        "filled by the source URL.")
                cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
            elif self.latency != StreamReader.DEFAULT_LATENCY:
                if OpenCVDep.gstreamer:
                    # Use a simple GStreamer pipeline to achieve low latency
                    pipeline = self._ADJUST_LATENCY_PIPELINE.format(
                        url=self.url,
                        latency=self.latency)
                    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
                else:
                    logging.warning(
                        "OpenCV was not compiled with GStreamer support. "
                        "Latency may be higher than requested.")

                    # Fall back to a normal FFmpeg configuration
                    cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
            else:
                # Use FFmpeg for a basic configuration. This is used in
                # case frame skipping is enabled. Someday we would like to
                # have frame skipping be possible with GStreamer.
                cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)

            if self._close_requested:
                return None, None

        # Try to get an initial frame several times, before giving up
        # DO NOT REMOVE. It seems like openCV likes to fail on the first frame,
        # but succeed on the second attempt. 5 attempts tried for robustness
        # sake, but are not empirically proven to be necessary.
        for n_tries in range(5):
            attempt_frame = cap.read()[1]
            if attempt_frame is not None:
                return cap, (time(), attempt_frame)

        # Close the capture, since it failed to get frames
        cap.release()
        return None, None

    _ADJUST_LATENCY_PIPELINE = (
        # Read from the stream at a specified url and latency
        "rtspsrc location={url} latency={latency} "
        # Depayload and decode the RTP data
        "! decodebin "
        # Convert the frame to a format OpenCV can accept
        "! videoconvert "
        # Make the frame available to OpenCV
        "! appsink"
    )
    """A pipeline for connecting to RTSP streams that allows for latency
    adjustments.
    """
