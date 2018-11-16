from brainframe.client.api import stubs


class API(stubs.AlertStubMixin,
          stubs.AnalysisStubMixin,
          stubs.EngineConfigurationStubMixin,
          stubs.IdentityStubMixin,
          stubs.PluginStubMixin,
          stubs.StreamStubMixin,
          stubs.ZoneStatusStubMixin,
          stubs.ZoneStubMixin,
          stubs.StorageStubMixin,
          stubs.ZoneAlarmStubMixin):
    """Provides access to BrainFrame API endpoints."""

    def __init__(self, server_url=None):
        """
        :param server_url: The URL of the BrainFrame instance to connect to. If
            None, it needs to be set later with set_url before use
        """
        super().__init__()
        self._server_url = server_url

    def set_url(self, server_url):
        self._server_url = server_url

    def close(self):
        """Clean up the API. It may no longer be used after this call."""
        stubs.StreamStubMixin.close(self)
