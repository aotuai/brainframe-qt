import logging
from typing import Dict, List

from PyQt5.QtCore import QObject

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
    """These video types are re-hosted by the server."""

    def __init__(self, *, parent: QObject):
        super().__init__(parent=parent)

        self._stream_readers: Dict[int, SyncedStreamReader] = {}
        self._async_closing_streams: List[SyncedStreamReader] = []
        """A list of StreamReader objects that are closing or may have finished
        closing"""

        self._init_signals()

    def _init_signals(self) -> None:
        self.destroyed.connect(self.close)

    def start_streaming(
        self,
        stream_config: StreamConfiguration,
        url: str
    ) -> SyncedStreamReader:
        """Starts reading from the stream using the given information, or returns an
        existing reader if we're already reading this stream.

        :param stream_config: The stream to connect to
        :param url: The URL to stream on
        :return: A Stream object
        """
        if not self.is_streaming(stream_config.id):
            # pipeline will be None if not in the options
            pipeline: str = stream_config.connection_options.get("pipeline")

            latency = StreamReader.DEFAULT_LATENCY
            if stream_config.connection_type in self.REHOSTED_VIDEO_TYPES:
                latency = StreamReader.REHOSTED_LATENCY

            gobject_init.start()

            # Streams created with a premises are always proxied from that premises
            is_proxied = stream_config.premises_id is not None

            stream_reader = GstStreamReader(
                url,
                latency=latency,
                runtime_options=stream_config.runtime_options,
                pipeline_str=pipeline,
                proxied=is_proxied)

            synced_stream_reader = SyncedStreamReader(
                stream_config.id,
                stream_reader,
                parent=self,
            )

            self._stream_readers[stream_config.id] = synced_stream_reader

        return self._stream_readers[stream_config.id]

    def is_streaming(self, stream_id: int) -> bool:
        """Checks if the the manager has a stream reader for the given stream
        id.

        :param stream_id: The stream ID to check
        :return: True if the stream manager has a stream reader, false
            otherwise
        """
        return stream_id in self._stream_readers

    def close_stream(self, stream_id: int) -> None:
        """Close a specific stream and remove the reference.

        :param stream_id: The ID of the stream to delete
        """
        stream = self.close_stream_async(stream_id)
        stream.wait_until_closed()

    def close(self) -> None:
        """Close all streams and remove references"""
        for stream_id in self._stream_readers.copy().keys():
            self.close_stream_async(stream_id)
        self._stream_readers = {}

        for stream in self._async_closing_streams:
            stream.wait_until_closed()
            self._async_closing_streams.remove(stream)

    def close_stream_async(self, stream_id: int) -> SyncedStreamReader:
        stream = self._stream_readers.pop(stream_id)
        self._async_closing_streams.append(stream)
        stream.close()
        return stream

    def delete_stream(self, stream_id: int, timeout: int = 120) -> None:
        api.delete_stream_configuration(stream_id, timeout=timeout)
        if self.is_streaming(stream_id):
            self.close_stream_async(stream_id)

    def get_stream_reader(self, stream_config: StreamConfiguration):
        """Get the SyncedStreamReader for the given stream_configuration.

        :param stream_config: The stream configuration to open.
        :return: A SyncedStreamReader object
        """
        url = api.get_stream_url(stream_config.id)
        logging.info("API: Opening stream on url " + url)

        return self.start_streaming(stream_config, url)
