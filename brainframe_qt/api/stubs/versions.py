from brainframe.client.api.stubs.stub import Stub


class VersionStubMixIn(Stub):
    """Provides stubs to call APIs related to getting the current BrainFrame
    version.
    """

    def version(self) -> str:
        """
        :return: The current BrainFrame version in the format X.Y.Z
        """
        req = f"/api/version"

        resp, _ = self._get_json(req)
        return resp
