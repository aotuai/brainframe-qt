import bisect
from dataclasses import dataclass
from threading import RLock
from typing import ClassVar, Dict, List, Optional, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from brainframe.client.api_utils.streaming import SyncedStreamReader
from brainframe.client.api_utils.streaming.processed_frame import \
    ProcessedFrame


@dataclass
class ReaderFrame:
    stream_reader: 'SyncedStreamReader'
    frame: 'ProcessedFrame'

    def __lt__(self, other: 'ReaderFrame'):
        return self.frame.tstamp < other.frame.tstamp


class SyncedFrameBuffer:
    MAX_BUF_SIZE: int = 300  # Arbitrary but not too big
    _buffer_lock: ClassVar[RLock] = RLock()

    combined_buffer: ClassVar[List[Tuple[ReaderFrame]]] = []

    split_buffers: ClassVar[Dict['SyncedStreamReader', List[ProcessedFrame]]]
    split_buffers = {}

    def __init__(self, stream_reader: 'SyncedStreamReader'):
        self.stream_reader = stream_reader
        self.split_buffers[stream_reader] = []

    def __del__(self):
        # This could be done by looping over self.pop, but this is faster
        with self._buffer_lock:
            # Filter all frames in queue and remove those belonging to
            # this instance's SyncedStreamReader
            self.combined_buffer = [
                reader_frame
                for reader_frame in self.combined_buffer
                if reader_frame.stream_reader is not self.stream_reader
            ]

            # Remove dict entry to this SyncedStreamReader entirely
            self.split_buffers.pop(self.stream_reader)

    def add_frame(self, frame: ProcessedFrame) -> None:
        with self._buffer_lock:
            while len(self.combined_buffer) >= self.MAX_BUF_SIZE:
                self._remove_oldest_frame()

            reader_frame = ReaderFrame(
                stream_reader=self.stream_reader,
                frame=frame
            )

            bisect.insort_left(self.combined_buffer, reader_frame)
            self.split_buffers[self.stream_reader].append(frame)

    def pop_oldest(self) -> ProcessedFrame:
        with self._buffer_lock:
            # Get oldest frame for stream
            frame = self.split_buffers[self.stream_reader].pop(0)

            reader_frame = ReaderFrame(
                stream_reader=self.stream_reader,
                frame=frame
            )

            # Remove it from combined deque
            # TODO: Test with really large buffer. Make sure not too
            #       computationally intensive
            self.combined_buffer.remove(reader_frame)

        return frame

    def pop_until(self, tstamp: float) -> Optional[ProcessedFrame]:
        oldest_frame: Optional[ProcessedFrame]
        buffer = self.split_buffers[self.stream_reader]

        with self._buffer_lock:
            while len(buffer):
                oldest_frame = buffer[0]

                # Buffer has caught up
                if oldest_frame.tstamp >= tstamp:
                    break

                self.pop_oldest()

        return oldest_frame

    def pop_if_older(self, tstamp: float) -> Optional[ProcessedFrame]:
        """Pop the oldest frame in the buffer if the its tstamp is older than
        the one supplied.

        :return: None if there are no frames, or if the oldest frame has a
                 newer timestamp. The ProcessedFrame, if it's older.

        """
        with self._buffer_lock:
            buffer = self.split_buffers[self.stream_reader]
            if not len(buffer):
                return None

            if buffer[0].tstamp <= tstamp:
                return self.pop_oldest()
            else:
                return None

    def _remove_oldest_frame(self) -> None:
        with self._buffer_lock:
            reader_frame = self.combined_buffer.pop(0)

            frame = reader_frame.frame
            stream_reader = reader_frame.stream_reader

            popped_frame = self.split_buffers[stream_reader].pop(0)
            assert frame == popped_frame
