import bisect
from dataclasses import dataclass
from threading import RLock
from typing import ClassVar, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from brainframe.client.api_utils.streaming import SyncedStreamReader
from brainframe.client.api_utils.streaming.zone_status_frame import \
    ZoneStatusFrame

_BUFFER_TYPE = List[ZoneStatusFrame]


@dataclass
class ReaderFrame:
    stream_reader: 'SyncedStreamReader'
    frame: 'ZoneStatusFrame'

    def __lt__(self, other: 'ReaderFrame'):
        return self.frame.tstamp < other.frame.tstamp


class SyncedFrameBuffer:
    MAX_BUF_SIZE: int = 300  # Arbitrary but not too big
    _buffer_lock: ClassVar[RLock] = RLock()

    combined_buffer: ClassVar[List[ReaderFrame]] = []
    instance_buffers: ClassVar[Dict['SyncedStreamReader', _BUFFER_TYPE]] = {}

    def __init__(self, stream_reader: 'SyncedStreamReader'):
        self.stream_reader = stream_reader
        self.instance_buffers[stream_reader] = []

    def __del__(self):
        # This could be done by looping over self.pop_oldest, but this is
        # faster
        with self._buffer_lock:
            # Filter all frames in queue and remove those belonging to
            # this instance's SyncedStreamReader
            type(self).combined_buffer = [
                reader_frame
                for reader_frame in self.combined_buffer
                if reader_frame.stream_reader is not self.stream_reader
            ]

            # Remove dict entry to this SyncedStreamReader entirely
            self.instance_buffers.pop(self.stream_reader)

    def add_frame(self, frame: ZoneStatusFrame) -> ZoneStatusFrame:

        popped_frame: Optional[ZoneStatusFrame] = None

        with self._buffer_lock:
            if len(self.combined_buffer) == self.MAX_BUF_SIZE:
                popped_frame = self.pop_oldest()
            assert len(self.combined_buffer) < self.MAX_BUF_SIZE

            reader_frame = ReaderFrame(
                stream_reader=self.stream_reader,
                frame=frame
            )

            bisect.insort_left(self.combined_buffer, reader_frame)
            self._instance_buffer.append(frame)

        return popped_frame

    def pop_oldest(self) -> ZoneStatusFrame:
        """Pop the oldest frame from this instance's buffer"""
        with self._buffer_lock:
            # Get oldest frame for stream
            frame = self._instance_buffer.pop(0)

            reader_frame = ReaderFrame(
                stream_reader=self.stream_reader,
                frame=frame
            )

            # TODO: Test with really large buffer. Make sure not too
            #       computationally intensive
            # Remove it from combined buffer
            self.combined_buffer.remove(reader_frame)

        return frame

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
            if not len(self._instance_buffer):
                return None

            oldest_frame = self._instance_buffer[0]

            if oldest_frame.tstamp < tstamp:
                # Pop the frame from both instance and combined buffers
                popped_frame = self.pop_oldest()
                assert oldest_frame is popped_frame

                return popped_frame
            else:
                return None

    def _remove_oldest_frame(self) -> None:
        with self._buffer_lock:
            reader_frame = self.combined_buffer.pop(0)

            frame = reader_frame.frame
            stream_reader = reader_frame.stream_reader

            # Note that we're popping a frame from a potentially different
            # instance's buffer
            popped_frame = self.instance_buffers[stream_reader].pop(0)
            assert frame is popped_frame

    @property
    def _instance_buffer(self) -> _BUFFER_TYPE:
        return self.instance_buffers[self.stream_reader]
