from threading import Thread


class StreamManager:
    """
    Keeps track of existing Stream objects, and
    """
    def __init__(self):
        # Keep a dict of {stream_id: stream} that have been opened
        pass

    def get_stream(self, stream_id):
        """Gets a specific stream object OR creates the connection and returns
        it if it does not already exist

        :param stream_id:
        :return: A Stream object
        """

    def close_stream(self, stream_id):
        """Close a specific stream and remove the reference """
        # Set 'stream.running' = False for that stream

    def close_all(self):
        """Close all streams and remove references"""
        # run self.close_stream for each stream id



class StatusPoller(Thread):
    """ This solves the problem that multiple UI elements will want to know the
    latest ZoneStatuses for any given stream. """
    def run(self):
        """Polls Brainserver for ZoneStatuses at a constant rate"""

    def get_latest(self, stream_id):
        """Returns the latest cached list of ZoneStatuses for that stream_id"""
        return self.__latest[stream_id]

    def close(self):
        """Close the status polling thread"""
        self.__running = False