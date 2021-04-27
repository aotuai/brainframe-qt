import typing
from threading import RLock
from typing import ClassVar, List, Optional
from weakref import WeakSet

from brainframe_qt.api_utils.streaming.zone_status_frame import \
    ZoneStatusFrame
from brainframe_qt.ui.resources.config import StreamingSettings


class SyncedFrameBuffer:
    GUARANTEED_BUFFER_SPACE: int = 30
    """Amount of space each buffer is allocated, even if total is over max"""

    _buffer_lock: ClassVar[RLock] = RLock()

    _instances = WeakSet()  # type: ClassVar[WeakSet[SyncedFrameBuffer]]

    _max_buffer_size: ClassVar[int] = 300
    """The maximum size of the shared frame buffer. This value is given a
    default for testing purposes but will be overridden by a user-configurable
    setting when run normally.
    """

    def __init__(self):
        self._buffer: List[ZoneStatusFrame] = []
        self._instances.add(self)

        self.streaming_settings = StreamingSettings()
        self.set_max_buffer_size(self.streaming_settings.frame_buffer_size)

        self._init_signals()

    def __len__(self) -> int:
        return len(self._buffer)

    def _init_signals(self) -> None:
        self.streaming_settings.value_changed.connect(self._handle_settings_change)

    def add_frame(self, frame: ZoneStatusFrame) -> None:
        with self._buffer_lock:
            self._buffer.append(frame)

    @classmethod
    def set_max_buffer_size(cls, max_size: int) -> None:
        """Sets the shared maximum size of the frame buffer.

        If this value is decreased during runtime, the buffer will not
        immediately decrease in size. It will slowly decrease as frames are
        removed from the buffer.

        :param max_size: The new buffer size
        """
        cls._max_buffer_size = max_size

    @property
    def is_empty(self) -> bool:
        return not len(self)

    @property
    def is_full(self) -> bool:
        return self._total_length >= self._max_buffer_size

    @property
    def needs_guaranteed_space(self) -> bool:
        return len(self) < self.GUARANTEED_BUFFER_SPACE

    def pop_oldest(self) -> Optional[ZoneStatusFrame]:
        """Pop the oldest frame from this instance's buffer. None if buffer is
        empty"""
        with self._buffer_lock:
            if self.is_empty:
                return None

            # Get oldest frame for stream
            return self._buffer.pop(0)

    def pop_until(self, tstamp: float) -> Optional[ZoneStatusFrame]:
        """Pop frames until the provided oldest frame in the buffer is newer
        than the provided tstamp
        """
        oldest_frame: Optional[ZoneStatusFrame] = None

        with self._buffer_lock:
            while True:
                popped_frame = self.pop_if_older(tstamp)

                if not popped_frame:
                    break

                oldest_frame = popped_frame

        return oldest_frame

    def pop_if_older(self, tstamp: float) -> Optional[ZoneStatusFrame]:
        """Pop the oldest frame in the buffer if its tstamp is older than the
        one supplied.

        :return: None if there are no frames, or if the oldest frame has a
                 newer timestamp. The ZoneStatusFrame, if it's older.

        """
        with self._buffer_lock:
            if self.is_empty:
                return None

            oldest_frame = self._buffer[0]

            if oldest_frame.tstamp < tstamp:
                # Pop the frame from both instance and combined buffers
                popped_frame = self.pop_oldest()
                assert oldest_frame is popped_frame

                return popped_frame
            else:
                return None

    @property
    def _total_length(self) -> int:
        with self._buffer_lock:
            return sum(map(len, self._instances))

    def _handle_settings_change(self, setting: str, value: object):
        if setting == "frame_buffer_size":
            value = typing.cast(int, value)
            self.set_max_buffer_size(value)
