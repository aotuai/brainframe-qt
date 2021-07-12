import logging
import typing
from typing import Dict, List

from PyQt5.QtCore import QObject, QThread

from brainframe.api.bf_codecs import StreamConfiguration

from brainframe_qt.api_utils import api

from .synced_reader import SyncedStreamReader


class StreamManager(QObject):
    """Keeps track of existing Stream objects, and creates new ones as necessary"""

    _MAX_ACTIVE_STREAMS = 5
    """Number of streams to run concurrently"""

    def __init__(self, *, parent: QObject):
        super().__init__(parent=parent)

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
        stream_readers = self.stream_readers.values()
        for stream_reader in stream_readers:
            stream_reader.close()
        for stream_reader in stream_readers:
            stream_reader.wait_until_closed()
        logging.info("StreamManager close finished")

    def delete_stream(self, stream_id: int, timeout: int = 120) -> None:
        """[blocking API] Delete a stream through the API and initiate the closing of
        its corresponding StreamReader
        """
        self.stop_streaming(stream_id)
        api.delete_stream_configuration(stream_id, timeout=timeout)

    def pause_streaming(self, stream_id) -> None:
        stream_reader = self.stream_readers[stream_id]
        stream_reader.pause_streaming()

        if stream_id in self._running_streams:
            self._running_streams.remove(stream_id)

        self._paused_streams.insert(0, stream_id)

    def resume_streaming(self, stream_id) -> None:
        if stream_id in self._paused_streams:
            self._paused_streams.remove(stream_id)

        elif stream_id in self._running_streams:
            self._running_streams.remove(stream_id)

        # Insert the newest stream at the front of the queue
        self._running_streams.insert(0, stream_id)

        # Check if over max concurrent streams and pause the oldest if necessary
        # The while loop is here as a safety mechanism
        while len(self._running_streams) > self._MAX_ACTIVE_STREAMS:
            self.pause_streaming(self._running_streams[-1])

        # Resume the streaming if it was paused
        stream_reader = self.stream_readers[stream_id]
        if stream_reader.is_streaming_paused:
            stream_reader.resume_streaming()

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
        # Get the Stream Reader
        if stream_conf.id in self.stream_readers:
            # If it's paused, then run self._unpause_stream, otherwise, return it
            stream_reader = self.stream_readers[stream_conf.id]
        else:
            stream_reader = self._create_synced_reader(stream_conf, url)
            self.stream_readers[stream_conf.id] = stream_reader

        self.resume_streaming(stream_conf.id)

        return stream_reader

    def stop_streaming(self, stream_id: int) -> None:
        """Requests a stream to close asynchronously

        :param stream_id: The ID of the stream to delete
        """
        if stream_id in self._running_streams:
            self._running_streams.remove(stream_id)
        else:
            self._paused_streams.remove(stream_id)

        stream_reader = self.stream_readers[stream_id]
        stream_reader.close()

        # Removing references to Stream Reader is handled in _remove_stream_reference
        # slot asynchronously

    def _create_synced_reader(
        self, stream_conf: StreamConfiguration, url: str
    ) -> SyncedStreamReader:

        synced_stream_reader = SyncedStreamReader(
            stream_conf,
            url,
            # No parent if moving to a different thread
            parent=typing.cast(QObject, None),
        )

        thread = QThread(parent=self)

        synced_stream_reader.moveToThread(thread)
        thread.started.connect(synced_stream_reader.run)

        # Quit the thread when the StreamReader is done operating
        synced_stream_reader.finished.connect(thread.quit)

        # Delete the thread when its done operating
        thread.finished.connect(thread.deleteLater)

        # When StreamReader is done, remove it from the collection that tracks them
        synced_stream_reader.finished.connect(
            lambda: self._handle_dereference(stream_conf.id)
        )

        thread.start()

        return synced_stream_reader

    def _handle_dereference(self, stream_id: int) -> None:
        self.stream_readers.pop(stream_id)

        # Remove reference if stream is running, resuming another stream if available
        if stream_id in self._running_streams:
            self._running_streams.remove(stream_id)

            if len(self._paused_streams) > 0:
                self.resume_streaming(self._paused_streams[0])

        # Remove reference if stream is paused
        elif stream_id in self._paused_streams:
            self._paused_streams.remove(stream_id)
