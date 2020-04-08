from brainframe.client.api.status_receiver import StatusReceiver
from brainframe.client.api.codecs import StreamConfiguration
from brainframe.shared.stream_reader import StreamReader
from brainframe.shared.gstreamer.stream_reader import GstStreamReader
from brainframe.shared.gstreamer import gobject_init

from .synced_reader import SyncedStreamReader


class StreamManager:
    """Keeps track of existing Stream objects, and creates new ones as
    necessary.
    """

    REHOSTED_VIDEO_TYPES = [StreamConfiguration.ConnType.WEBCAM,
                            StreamConfiguration.ConnType.FILE]
    """These video types are re-hosted by the server."""

    def __init__(self, status_receiver: StatusReceiver):
        self._stream_readers = {}
        self._status_receiver = status_receiver
        self._async_closing_streams = []
        """A list of StreamReader objects that are closing or may have finished
        closing"""

    def start_streaming(self,
                        stream_config: StreamConfiguration,
                        url: str) -> SyncedStreamReader:
        """Starts reading from the stream using the given information, or
        returns an existing reader if we're already reading this stream.

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

            # Streams created with a premises are always proxied from that
            # premises
            proxied = stream_config.premises_id is not None

            stream_reader = GstStreamReader(
                url,
                latency=latency,
                runtime_options=stream_config.runtime_options,
                pipeline=pipeline,
                proxied=proxied)
            synced_stream_reader = SyncedStreamReader(
                stream_config.id,
                stream_reader,
                self._status_receiver)
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
