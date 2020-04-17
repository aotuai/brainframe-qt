from typing import Tuple
from time import sleep, time

from requests.exceptions import ConnectionError, ReadTimeout

from brainframe.client.api import stubs, api_errors
from brainframe.client.api.stubs.base_stub import DEFAULT_TIMEOUT


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
          stubs.PremisesStubMixin,
          stubs.UserStubMixin,
          stubs.LicenseStubMixIn):
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
        timeout_api._status_receiver = self._status_receiver
        timeout_api._timeout = timeout

        return timeout_api

    def version(self, timeout=DEFAULT_TIMEOUT) -> str:
        """
        :return: The current BrainFrame version in the format X.Y.Z
        """
        req = f"/api/version"

        resp, _ = self._get_json(req, timeout)
        return resp

    def wait_for_server_initialization(self, timeout: int = None):
        """
        :param timeout: In this case, the 'timeout' is the maximum amount
        of time to wait. If None, this function will hang forever. If set to
        an integer, the function will raise a TimeoutError after the server
        did not connect in the appropriate amount of time.

        This function is typically used in scripts that might be run by devs
        who are starting the BrainFrame Server often.
        """
        start_time = time()
        while True:
            if timeout is not None and time() - start_time > timeout:
                raise TimeoutError("The server did not start in time!")

            try:
                # Test connection to server
                self.version()
                # TODO: Remove this check and let the user know about the
                #       license not being valid
                license_info = self.get_license_info()
                if license_info.state == license_info.State.VALID:
                    break
            except (ConnectionError, ConnectionRefusedError,
                    api_errors.UnauthorizedError, ReadTimeout):
                # Server not started yet or there is a communication
                # error
                pass
            except api_errors.UnknownError as exc:
                if exc.status_code not in [502]:
                    raise

            # Prevent busy loop
            sleep(.1)

    def close(self):
        """Clean up the API. It may no longer be used after this call."""
        stubs.StreamStubMixin.close(self)
