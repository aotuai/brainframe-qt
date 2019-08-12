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
          stubs.VersionStubMixIn):
    """Provides access to BrainFrame API endpoints."""

    def __init__(self, server_url=None, credentials: Tuple[str, str] = None):
        """
        :param server_url: The URL of the BrainFrame instance to connect to. If
            None, it needs to be set later with set_url before use
        :param credentials: The username and password as a tuple
        """
        super().__init__()
        self._server_url = server_url
        self._credentials = credentials

    def close(self):
        """Clean up the API. It may no longer be used after this call."""
        stubs.StreamStubMixin.close(self)
