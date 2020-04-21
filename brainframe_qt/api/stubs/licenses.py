import ujson

from brainframe.client.api.stubs.base_stub import BaseStub, DEFAULT_TIMEOUT
from brainframe.client.api.codecs import LicenseInfo


class LicenseStubMixIn(BaseStub):
    """Provides stubs to call APIs for uploading license keys and getting
    the server's license status.
    """

    def get_license_info(self, timeout=DEFAULT_TIMEOUT) -> LicenseInfo:
        """Gets licensing information from the server.

        :param timeout: The timeout to use for this request
        :return: License info
        """
        req = "/api/license"

        license_info, _ = self._get_json(req, timeout)
        return LicenseInfo.from_dict(license_info)

    def set_license_key(self, license_key: str, timeout=DEFAULT_TIMEOUT) \
            -> LicenseInfo:
        """Uploads a license key to the server and applies it.

        :param license_key: A base64-encoded string of license data
        :param timeout: The timeout to use for this request
        :return: License info after the key is applied
        """
        req = "/api/license"

        resp = self._put(req, timeout,
                         data=license_key,
                         content_type="application/base64")
        license_info = ujson.loads(resp.content)
        return LicenseInfo.from_dict(license_info)
