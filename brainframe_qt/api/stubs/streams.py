from typing import List, Optional
import logging

from brainframe.client.api import api_errors
from brainframe.client.api.codecs import StreamConfiguration
from brainframe.client.api.stubs.stub import Stub
from brainframe.client.api.streaming import (
    StreamManager, StatusPoller)
from brainframe.client.api.synced_reader import SyncedStreamReader


class StreamStubMixin(Stub):
    """Provides stubs for calling stream-related APIs and managing
    stream-related client objects.
    """

    def __init__(self):
        # These are evaluated lazily
        self._stream_manager = None
        self._status_poller = None

    def get_status_poller(self) -> StatusPoller:
        """Returns the singleton StatusPoller object"""
        if self._status_poller is None or not self._status_poller.is_running:
            self._status_poller = StatusPoller(self, 33)
        return self._status_poller

    def get_stream_manager(self) -> StreamManager:
        """Returns the singleton StreamManager object"""
        if self._stream_manager is None:
            self._stream_manager = StreamManager(self.get_status_poller())
        return self._stream_manager

    def get_stream_configurations(self) -> List[StreamConfiguration]:
        """Get all StreamConfigurations that currently exist.

        :return: [StreamConfiguration, StreamConfiguration, ...]
        """
        req = "/api/streams/"
        data = self._get(req)

        configs = [StreamConfiguration.from_dict(d) for d in data]
        return configs

    def set_stream_configuration(self, stream_configuration) \
            -> Optional[StreamConfiguration]:
        """Update an existing stream configuration or create a new one
        If creating a new one, the stream_configuration.id will be None
        :param stream_configuration: StreamConfiguration
        :return: StreamConfiguration, initialized with an ID
        """
        req = "/api/streams/"
        data = self._post_codec(req, stream_configuration)
        config = StreamConfiguration.from_dict(data)
        return config

    def delete_stream_configuration(self, stream_id):
        """Deletes a stream configuration with the given ID. Also stops
        analysis if analysis was running and closes the stream.

        :param stream_id: The ID of the stream to delete
        """
        req = f"/api/streams/{stream_id}"
        self._delete(req)
        if self._stream_manager is not None:
            self._stream_manager.close_stream(stream_id)

    def get_stream_reader(self, stream_config: StreamConfiguration) \
            -> Optional[SyncedStreamReader]:
        """Get the SyncedStreamReader for the given stream_configuration.

        :param stream_config: The stream configuration to open.
        :return: A SyncedStreamReader object OR None, if the server was unable
            to open a stream.
        """
        req = f"/api/streams/{stream_config.id}/url"
        try:
            url = self._get(req)
        except api_errors.StreamNotFoundError:
            logging.warning("API: Requested stream that doesn't exist!")
            return None

        logging.info("API: Opening stream on url " + url)

        return self.get_stream_manager().start_streaming(
            stream_config,
            url)

    def close(self):
        if self._status_poller is not None:
            self._status_poller.close()
            self._status_poller = None
        if self._stream_manager is not None:
            self._stream_manager.close()
            self._stream_manager = None
