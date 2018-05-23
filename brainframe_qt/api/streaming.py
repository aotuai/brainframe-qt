import logging
from typing import List, Tuple, Union
from threading import Thread
from time import sleep, time

import cv2

from brainframe.client.api import codecs
from brainframe.client.api.codecs import StreamConfiguration


class StatusPoller(Thread):
    """ This solves the problem that multiple UI elements will want to know the
    latest ZoneStatuses for any given stream. """

    def __init__(self, api, ms_status_updates):
        """
        :param api: An API() object for interacting with the BrainFrame REST
        api.
        :param ms_status_updates: Miliseconds between calling for a zone status
        update
        """
        super().__init__(name="StatusPollerThread")
        self._api = api
        self._seconds_between_updates = ms_status_updates / 1000
        self._running = False

        # Get something before starting the thread
        self._latest = self._api.get_latest_zone_statuses()
        self.start()

    def run(self):
        """Polls Brainserver for ZoneStatuses at a constant rate"""
        self._running = True
        call_time = 0
        while self._running:

            # Call the server, timing how long the call takes
            try:
                start = time()
                latest = self._api.get_latest_zone_statuses()
                self._latest = latest
                call_time = time() - start
            except ConnectionError:
                logging.warning("StatusLogger: Could not reach server!")
                sleep(2)

            # Sleep for the appropriate amount to keep call times consistent
            time_left = self._seconds_between_updates - call_time
            if time_left > 0:
                sleep(time_left)

        self._running = False

    @property
    def is_running(self):
        return self._running

    def get_alarm(self, stream_id, alarm_id) -> Union[None, codecs.ZoneAlarm]:
        """Return a list of unverified alerts for this stream_id"""
        zones = self.get_zones(stream_id)
        if len(zones) == 0:
            return None
        alarms = sum([zone.alarms for zone in zones], [])
        alarms = [alarm for alarm in alarms if alarm.id == alarm_id]
        if len(alarms) == 0:
            return None
        return alarms[0]

    def get_zones(self, stream_id) -> List[codecs.Zone]:
        statuses = self.get_latest_statuses(stream_id)
        zones = [status.zone for status in statuses]
        return zones

    def get_detections(self, stream_id) -> Tuple[float, List[codecs.Detection]]:
        """Conveniently return all detections found in this stream and
        their respective timestamp in which they were detected."""
        statuses = self.get_latest_statuses(stream_id)
        if len(statuses) == 0:
            return 0, []

        # Find the main screen
        status = [status for status in statuses
                  if status.zone.name == "Screen"][0]
        return status.tstamp, status.detections

    def get_latest_statuses(self, stream_id) -> List[codecs.ZoneStatus]:
        """Returns the latest cached list of ZoneStatuses for that stream_id"""
        latest = self._latest
        if stream_id not in latest:
            return []
        return latest[stream_id]

    def close(self):
        """Close the status polling thread"""
        self._running = False
        self.join()


class ProcessedFrame:
    """A frame that may or may not have undergone processing on the server."""

    def __init__(self, frame, tstamp, zone_statuses):
        self.frame = frame
        self.tstamp = tstamp
        self.zone_statuses = zone_statuses


class SyncedStreamReader(Thread):
    """Reads frames from a stream and syncs them up with zone statuses."""

    MAX_BUF_SIZE = 1000

    def __init__(self,
                 url: str,
                 stream_config: StreamConfiguration,
                 status_poller: StatusPoller):
        """Creates a new SyncedStreamReader.

        :param url: The URL of the stream to read from
        :param stream_config: The StreamConfiguration for this stream
        :param status_poller: The StatusPoller currently in use
        """
        super().__init__(name="SyncedStreamReaderThread")
        self.url = url
        self.stream_config = stream_config
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
        if latest is not None:
            rgb = cv2.cvtColor(latest.frame, cv2.COLOR_BGR2RGB)
            latest = ProcessedFrame(rgb, latest.tstamp, latest.zone_statuses)
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

            # Get the latest zone statuses
            zone_statuses = self.status_poller.get_latest_statuses(
                self.stream_config.id)
            tstamp = zone_statuses[-1].tstamp if zone_statuses else None

            if zone_statuses and last_inference_tstamp != tstamp:
                # Catch up to the previous inference frame
                while frame_buf[0].tstamp <= last_inference_tstamp:
                    frame_buf.pop(0)

                last_inference_tstamp = tstamp

            # If we have inference later than the current frame, update the
            # current frame
            if frame_buf and frame_buf[0].tstamp <= last_inference_tstamp:
                frame = frame_buf.pop(0)
                self._latest = ProcessedFrame(
                    frame.frame,
                    frame.tstamp,
                    zone_statuses)

            # Drain the buffer if it is getting too large
            while len(frame_buf) > self.MAX_BUF_SIZE:
                frame_buf.pop(0)

        logging.info("SyncedStreamReader: Closing")
        self._running = False

    def _update_latest(self, zone_statuses):
        """Check if the zone statuses correspond to any frames in the buffer and
        update the latest if so.
        """

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
                url, stream_config, self._status_poller)
            self._stream_readers[url] = stream_reader
            return stream_reader

        if not self._stream_readers[url].is_running:
            # Stream not running. Starting a new one.
            self._stream_readers[url].close()
            stream_reader = SyncedStreamReader(
                url, stream_config, self._status_poller)
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
