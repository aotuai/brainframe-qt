from brainframe.client.api.status_poller import StatusPoller
from brainframe.client.api.codecs import StreamConfiguration
from brainframe.shared.stream_reader import StreamReader
from .synced_reader import SyncedStreamReader
from brainframe.shared.gstreamer.stream_reader import GstStreamReader


class StreamManager:
    """Keeps track of existing Stream objects, and creates new ones as
    necessary.
    """

    REHOSTED_VIDEO_TYPES = [StreamConfiguration.ConnType.WEBCAM,
                            StreamConfiguration.ConnType.FILE]
    """These video types are re-hosted by the server."""

    def __init__(self, status_poller: StatusPoller):
        self._stream_readers = {}
        self._status_poller = status_poller

    def start_streaming(self,
                        stream_config: StreamConfiguration,
                        url: str) -> SyncedStreamReader:
        """Starts reading from the stream using the given information, or
        returns an existing reader if we're already reading this stream.

        :param stream_config: The stream to connect to
        :param url: The URL to stream on
        :return: A Stream object
        """
        if stream_config.id not in self._stream_readers:
            pipeline = None
            if "pipeline" in stream_config.connection_options:
                pipeline = stream_config.connection_options["pipeline"]

            latency = StreamReader.DEFAULT_LATENCY
            if stream_config.connection_type in self.REHOSTED_VIDEO_TYPES:
                latency = StreamReader.REHOSTED_LATENCY

            stream_reader = GstStreamReader(
                url,
                latency=latency,
                runtime_options=stream_config.runtime_options,
                pipeline=pipeline)
            synced_stream_reader = SyncedStreamReader(
                stream_config.id,
                stream_reader,
                self._status_poller)
            self._stream_readers[stream_config.id] = synced_stream_reader

        return self._stream_readers[stream_config.id]

    def close_stream(self, stream_id):
        """Close a specific stream and remove the reference.

        :param stream_id: The ID of the stream to delete
        """
        stream = self._close_stream_async(stream_id)
        stream.wait_until_closed()

    def close(self):
        """Close all streams and remove references"""
        closing_streams = []
        for stream_id in self._stream_readers.copy().keys():
            closing_streams.append(self._close_stream_async(stream_id))
        self._stream_readers = {}

        for stream in closing_streams:
            stream.wait_until_closed()

    def _close_stream_async(self, stream_id) -> SyncedStreamReader:
        stream = self._stream_readers.pop(stream_id)
        stream.close()
        return stream
