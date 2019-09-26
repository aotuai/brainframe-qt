from brainframe.client.api.stubs.base_stub import BaseStub, DEFAULT_TIMEOUT


class VersionStubMixIn(BaseStub):
    """Provides stubs to call APIs related to getting the current BrainFrame
    version.
    """

    def version(self, timeout=DEFAULT_TIMEOUT) -> str:
        """
        :return: The current BrainFrame version in the format X.Y.Z
        """
        req = f"/api/version"

        resp, _ = self._get_json(req, timeout)
        return resp
