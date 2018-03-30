from threading import Thread
from time import sleep

from visionapp.shared.stream_capture import StreamReader


class StreamManager:
    """
    Keeps track of existing Stream objects, and
    """

    def __init__(self):
        self._stream_readers = {}

    def get_stream(self, url: str) -> StreamReader:
        """Gets a specific stream object OR creates the connection and returns
        it if it does not already exist

        :param url: The URL of the stream to connect to
        :return: A Stream object
        """
        if url not in self._stream_readers:
            stream_reader = StreamReader(url)
            self._stream_readers[url] = stream_reader
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
        print("Closing Stream manager")
        self._stream_readers = {}


class StatusPoller(Thread):
    """ This solves the problem that multiple UI elements will want to know the
    latest ZoneStatuses for any given stream. """

    def __init__(self, get_latest_statuses_func, ms_between_updates: int):
        """
        :param get_latest_statuses_func: A function returning the latest
        zone statuses, passed in by the API
        :param ms_between_updates: Miliseconds between calling for an update
        """
        super().__init__(name="StatusPollerThread")
        self._get_latest_zone_statuses = get_latest_statuses_func
        self._ms_between_updates = ms_between_updates / 1000
        self._running = False

        # Get something before starting the thread
        self._latest = self._get_latest_zone_statuses
        self.start()

    def run(self):
        """Polls Brainserver for ZoneStatuses at a constant rate"""
        self._running = True
        while self._running:
            self._latest = self._get_latest_zone_statuses()
            sleep(self._ms_between_updates)

        self._running = False

    def get_detections(self, stream_id):
        """Conveniently return all detections found in this stream"""
        latest = self._latest
        statuses = latest[stream_id]

        # Find the main screen
        status = [status for status in statuses
                  if status.zone.name == "Screen"][0]
        return status.detections

    def get_latest_statuses(self, stream_id):
        """Returns the latest cached list of ZoneStatuses for that stream_id"""
        latest = self._latest
        if stream_id not in latest:
            return []
        return latest[stream_id]

    def close(self):
        """Close the status polling thread"""
        self._running = False
        self.join()