import logging
import typing
from threading import RLock
from typing import Dict, List, Optional

from PyQt5.QtCore import QObject

from brainframe.api.bf_codecs import StreamConfiguration

from brainframe_qt.api_utils import api
from .synced_reader import SyncedStreamReader


class StreamManager(QObject):
    """Keeps track of existing Stream objects, and creates new ones as necessary"""

    _MAX_ACTIVE_STREAMS = 5
    """Number of streams to run concurrently"""

    def __init__(self, *, parent: QObject):
        super().__init__(parent=parent)

        self._stream_lock = RLock()

        self._running_streams: List[int] = []
        """Currently running streams. Does not include stay-alive streams.
        
        Max length should be _NUM_ACTIVE_STREAMS
        """
        self._paused_streams: List[int] = []
        """Currently paused streams"""

        self.stream_readers: Dict[int, SyncedStreamReader] = {}
        """All StreamReaders currently instantiated, paused or unpaused"""

        self._init_signals()

    def _init_signals(self) -> None:
        self.destroyed.connect(self.close)

    def close(self) -> None:
        """Request and wait for all streams to close"""
        logging.info("Initiating StreamManager close")
        self._close()
        logging.info("StreamManager close finished")

    def delete_stream(self, stream_id: int, timeout: int = 120) -> None:
        """[blocking API] Delete a stream through the API and initiate the closing of
        its corresponding StreamReader
        """
        api.delete_stream_configuration(stream_id, timeout=timeout)
        self.stop_streaming(stream_id)

    def pause_streaming(self, stream_id) -> None:
        self._set_stream_paused(stream_id, True)
        self._ensure_running_streams()

    def resume_streaming(self, stream_id) -> None:
        self._set_stream_paused(stream_id, False)
        self._ensure_running_streams()

    def start_streaming(
            self,
            stream_conf: StreamConfiguration,
            url: str,
    ) -> SyncedStreamReader:
        """Starts reading from the stream using the given information, or returns an
        existing reader if we're already reading this stream.

        :param stream_conf: The stream to connect to
        :param url: The URL to stream on
        :return: A SyncedStreamReader for the stream
        """
        return self._start_stream(stream_conf, url)

    def stop_streaming(self, stream_id: int) -> None:
        """Requests a stream to close asynchronously

        :param stream_id: The ID of the stream to delete
        """
        self._stop_stream(stream_id)
        self._ensure_running_streams()

    def _close(self) -> None:
        with self._stream_lock:
            streams = self.stream_readers.copy()
            for stream_id, stream_reader in streams.items():
                self._stop_stream(stream_id)
                stream_reader.wait_until_closed()

    def _create_synced_reader(
            self, stream_conf: StreamConfiguration, url: str
    ) -> SyncedStreamReader:

        synced_stream_reader = SyncedStreamReader(
            stream_conf,
            url,
            # No parent if moving to a different thread
            parent=typing.cast(QObject, None),
        )

        return synced_stream_reader

    def _ensure_running_streams(self) -> None:
        """Pause/unpause streams if over/under max"""
        with self._stream_lock:
            while (
                len(self._running_streams) < self._MAX_ACTIVE_STREAMS
                and self._paused_streams
            ):
                self._set_stream_paused(self._paused_streams[0], False)

            for _running_stream_id in self._running_streams[self._MAX_ACTIVE_STREAMS:]:
                self._set_stream_paused(_running_stream_id, paused=True)

    def _forget_stream(self, stream_id: int) -> None:
        with self._stream_lock:
            self._set_stream_paused(stream_id, paused=True)

            self._paused_streams.remove(stream_id)
            self.stream_readers.pop(stream_id)

    def _get_stream_reader(
        self,
        stream_conf: StreamConfiguration,
        url: str,
    ) -> Optional[SyncedStreamReader]:
        with self._stream_lock:
            if stream_conf.id in self.stream_readers:
                # If it's paused, then run self._unpause_stream, otherwise, return it
                stream_reader = self.stream_readers[stream_conf.id]
            else:
                stream_reader = self._create_synced_reader(stream_conf, url)
                self.stream_readers[stream_conf.id] = stream_reader

        return stream_reader

    def _set_stream_paused(self, stream_id: int, paused: bool) -> None:
        with self._stream_lock:
            stream_reader = self.stream_readers[stream_id]

            if paused:
                stream_reader.pause_streaming()
                destination_list = self._paused_streams
            else:
                stream_reader.resume_streaming()
                destination_list = self._running_streams

            if stream_id in self._paused_streams:
                self._paused_streams.remove(stream_id)
            if stream_id in self._running_streams:
                self._running_streams.remove(stream_id)

            destination_list.insert(0, stream_id)

    def _start_stream(
            self,
            stream_conf: StreamConfiguration,
            url: str,
    ) -> SyncedStreamReader:
        with self._stream_lock:
            stream_reader = self._get_stream_reader(stream_conf, url)

            if stream_conf.id not in self._running_streams:
                self._set_stream_paused(stream_conf.id, False)

            self._ensure_running_streams()

        return stream_reader

    def _stop_stream(self, stream_id: int) -> None:
        with self._stream_lock:
            stream_reader = self.stream_readers[stream_id]
            self._forget_stream(stream_id)
            stream_reader.close()
