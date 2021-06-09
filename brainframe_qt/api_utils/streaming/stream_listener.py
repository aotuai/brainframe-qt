from threading import Event

from PyQt5.QtCore import QObject


class StreamListener(QObject):
    """This is used by SyncedStreamReader to pass events to the UI"""

    def __init__(self, parent: QObject):
        super().__init__(parent=parent)

        self.frame_event = Event()
        """Called when a new ZoneStatusFrame is ready"""

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
