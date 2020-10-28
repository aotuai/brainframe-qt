from threading import RLock
from typing import ClassVar, List, Optional
from weakref import WeakSet

from brainframe.client.api_utils.streaming.zone_status_frame import \
    ZoneStatusFrame


class SyncedFrameBuffer:
    MAX_BUF_SIZE: int = 300  # Arbitrary but not too big
    GUARANTEED_BUFFER_SPACE: int = 30
    """Amount of space each buffer is allocated, even if total is over max"""

    _buffer_lock: ClassVar[RLock] = RLock()

    _instances = WeakSet()  # type: ClassVar[WeakSet[SyncedFrameBuffer]]

    def __init__(self):
        self._buffer: List[ZoneStatusFrame] = []
        self._instances.add(self)

    def __len__(self) -> int:
        return len(self._buffer)

    def add_frame(self, frame: ZoneStatusFrame) -> None:
        with self._buffer_lock:
            self._buffer.append(frame)

    @property
    def is_empty(self) -> bool:
        return not len(self)

    @property
    def is_full(self) -> bool:
        return self._total_length >= self.MAX_BUF_SIZE

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
                 newer timestamp. The ProcessedFrame, if it's older.

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
