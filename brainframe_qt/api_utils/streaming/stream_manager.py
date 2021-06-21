import logging
import typing
from typing import Dict, Optional

from PyQt5.QtCore import QObject, QThread

from brainframe.api.bf_codecs import StreamConfiguration
from gstly import gobject_init
from gstly.gst_stream_reader import GstStreamReader
from gstly.abstract_stream_reader import StreamReader

from brainframe_qt.api_utils import api

from .synced_reader import SyncedStreamReader


class StreamManager(QObject):
    """Keeps track of existing Stream objects, and creates new ones as necessary"""

    REHOSTED_VIDEO_TYPES = [
        StreamConfiguration.ConnType.WEBCAM,
        StreamConfiguration.ConnType.FILE,
    ]
    """Video types that are re-hosted by the server"""

    def __init__(self, *, parent: QObject):
        super().__init__(parent=parent)

        self._stream_readers: Dict[int, SyncedStreamReader] = {}

        self._init_signals()

    def _init_signals(self) -> None:
        self.destroyed.connect(self.close)

    def start_streaming(
        self,
        stream_conf: StreamConfiguration,
        url: str
    ) -> SyncedStreamReader:
        """Starts reading from the stream using the given information, or returns an
        existing reader if we're already reading this stream.

        :param stream_conf: The stream to connect to
        :param url: The URL to stream on
        :return: A SyncedStreamReader for the stream
        """
        if not self.is_streaming(stream_conf.id):
            synced_stream_reader = self._create_synced_reader(stream_conf, url)
            self._stream_readers[stream_conf.id] = synced_stream_reader

        return self._stream_readers[stream_conf.id]

    def is_streaming(self, stream_id: int) -> bool:
        """Checks if the the manager has a stream reader for the given stream id.

        :param stream_id: The stream ID to check
        :return: True if the stream manager has a stream reader, False otherwise
        """
        return stream_id in self._stream_readers

    def close_stream(self, stream_id: int) -> None:
        """Requests a stream to close asynchronously

        :param stream_id: The ID of the stream to delete
        """
        stream_reader = self._stream_readers[stream_id]
        stream_reader.close()

    def close(self) -> None:
        """Request and wait for all streams to close"""
        logging.info("Initiating StreamManager close")
        stream_readers = self._stream_readers.values()
        for stream_reader in stream_readers:
            stream_reader.close()
        for stream_reader in stream_readers:
            stream_reader.wait_until_closed()
        logging.info("StreamManager close finished")

    def delete_stream(self, stream_id: int, timeout: int = 120) -> None:
        """Delete a stream through the API and initiate the closing of its corresponding
        StreamReader"""
        api.delete_stream_configuration(stream_id, timeout=timeout)
        if self.is_streaming(stream_id):
            # The stream is removed from self._stream_readers in a teardown callback
            self.close_stream(stream_id)

    def get_stream_reader(
        self, stream_config: StreamConfiguration
    ) -> SyncedStreamReader:
        """Get the SyncedStreamReader for the given stream_configuration.

        :param stream_config: The stream configuration to open.
        :return: A SyncedStreamReader object
        """
        url = api.get_stream_url(stream_config.id)
        logging.info(f"API: Opening stream on url {url}")

        return self.start_streaming(stream_config, url)

    def _create_synced_reader(
        self, stream_conf: StreamConfiguration, url: str
    ) -> SyncedStreamReader:
        pipeline: Optional[str] = stream_conf.connection_options.get("pipeline")

        latency = StreamReader.DEFAULT_LATENCY
        if stream_conf.connection_type in self.REHOSTED_VIDEO_TYPES:
            latency = StreamReader.REHOSTED_LATENCY

        gobject_init.start()

        # Streams created with a premises are always proxied from that premises
        is_proxied = stream_conf.premises_id is not None

        stream_reader = GstStreamReader(
            url,
            latency=latency,
            runtime_options=stream_conf.runtime_options,
            pipeline_str=pipeline,
            proxied=is_proxied)

        synced_stream_reader = SyncedStreamReader(
            stream_conf.id,
            stream_reader,
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
            lambda: self._remove_stream_reference(stream_conf.id)
        )

        thread.start()

        return synced_stream_reader

    def _remove_stream_reference(self, stream_id: int) -> None:
        self._stream_readers.pop(stream_id)
