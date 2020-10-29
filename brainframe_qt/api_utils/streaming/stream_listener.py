from threading import Event


class StreamListener:
    """This is used by SyncedStreamReader to pass events to the UI"""

    def __init__(self):
        self.frame_event = Event()
        """Called when a new ProcessedFrame is ready"""

        self.stream_initializing_event = Event()
        """Called when the stream starts initializing"""

        self.stream_halted_event = Event()
        """Called when the stream has halted"""

        self.stream_closed_event = Event()
        """Called when the stream connection has closed"""

        self.stream_error_event = Event()
        """Called upon serious error (this shouldn't happen?)"""

    def clear_all_events(self):
        self.frame_event.clear()
        self.stream_initializing_event.clear()
        self.stream_halted_event.clear()
        self.stream_closed_event.clear()
        self.stream_error_event.clear()
