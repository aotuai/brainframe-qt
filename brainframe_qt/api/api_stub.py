from typing import Tuple

from brainframe.client.api import stubs


class API(stubs.AlertStubMixin,
          stubs.AnalysisStubMixin,
          stubs.IdentityStubMixin,
          stubs.PluginStubMixin,
          stubs.StreamStubMixin,
          stubs.ZoneStatusStubMixin,
          stubs.ZoneStubMixin,
          stubs.StorageStubMixin,
          stubs.ZoneAlarmStubMixin,
          stubs.ProcessImageStubMixIn,
          stubs.EncodingStubMixIn,
          stubs.VersionStubMixIn,
          stubs.PremisesStubMixin):
    """Provides access to BrainFrame API endpoints."""

    def __init__(self, server_url=None, credentials: Tuple[str, str] = None,
                 timeout=10):
        """
        :param server_url: The URL of the BrainFrame instance to connect to. If
            None, it needs to be set later with set_url before use
        :param credentials: The username and password as a tuple
        :param timeout: The timeout to use on requests
        """
        super().__init__()
        self._server_url = server_url
        self._credentials = credentials
        self._timeout = timeout

    def with_timeout(self, timeout: int) -> "API":
        """Creates a copy of this API object that is configured with the given
        timeout. This method allows timeouts to be set without affecting API
        calls on other threads.

        >>> api = API("http://my_brainframe.com")
        >>> api.get_stream_configurations()  # Use default timeout
        >>> timeout_api = api.with_timeout(100)
        >>> timeout_api.delete_stream_configuration(1)  # Known slow operation

        :param timeout: The timeout to set on the API copy
        :return: A copy of this API object with the configured timeout
        """
        timeout_api = API(self._server_url, self._credentials)

        timeout_api._stream_manager = self._stream_manager
        timeout_api._status_poller = self._status_poller
        timeout_api._timeout = timeout

        return timeout_api

    def close(self):
        """Clean up the API. It may no longer be used after this call."""
        stubs.StreamStubMixin.close(self)
