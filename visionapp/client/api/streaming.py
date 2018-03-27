from threading import Thread

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
        for _, stream_reader in self._stream_readers.items():
            stream_reader.close()

        self._stream_readers = {}


class StatusPoller(Thread):
    """ This solves the problem that multiple UI elements will want to know the
    latest ZoneStatuses for any given stream. """
    def __init__(self):
        super().__init__(name="StatusPollerThread")

    def run(self):
        """Polls Brainserver for ZoneStatuses at a constant rate"""

    def get_latest(self, stream_id):
        """Returns the latest cached list of ZoneStatuses for that stream_id"""
        return self.__latest[stream_id]

    def close(self):
        """Close the status polling thread"""
        self.__running = False

