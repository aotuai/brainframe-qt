from typing import Tuple
import ujson
import requests
import logging

from brainframe.client.api import api_errors
from brainframe.shared import error_kinds
from brainframe.client.api.codecs import Codec


class Stub:
    # For testing purposes
    get = staticmethod(requests.get)
    put = staticmethod(requests.put)
    post = staticmethod(requests.post)
    delete = staticmethod(requests.delete)

    def _get(self, api_url, params=None):
        """Send a GET request to the given URL.
        :param api_url: The /api/blah/blah to append to the base_url
        :param params: The "query_string" to add to the url. In the format
        of a dict, {"key": "value", ...} key and val must be a string
        :return: The JSON response as a dict, or None if none was sent
        """
        resp = self.get(self._full_url(api_url), params=params)
        if not resp.ok:
            raise _make_api_error(resp.content)

        if resp.content:
            return ujson.loads(resp.content)
        return None

    def _get_raw(self, api_url, params=None) -> Tuple[bytes, str]:
        """Send a GET request to the given URL.
        :param api_url: The /api/blah/blah to append to the base_url
        :param params: The "query_string" to add to the url. In the format
        of a dict, {"key": "value", ...} key and val must be a string
        :return: The raw bytes of the response and the content type
        """
        resp = self.get(self._full_url(api_url), params=params)
        if not resp.ok:
            raise _make_api_error(resp.content)

        return resp.content, resp.headers["content-type"]

    def _put_raw(self, api_url, data: bytes, content_type: str):
        """Send a PUT request to the given URL.
        :param api_url: The /api/blah/blah to append to the base url
        :param data: The raw data to send
        :param content_type: The mime type of the data being sent
        :return: The JSON response as a dict, or None of none was sent
        """
        resp = self.put(self._full_url(api_url),
                        data=data,
                        headers={'content-type': content_type})
        if not resp.ok:
            raise _make_api_error(resp.content)

        if resp.content:
            return ujson.loads(resp.content)
        return None

    def _put_codec(self, api_url, codec: Codec):
        """Send a PUT request to the given URL.
        :param api_url: The /api/blah/blah to append to the base_url
        :param codec: A codec to convert to JSON and send
        :return: The JSON response as a dict, or None if none was sent
        """
        data = codec.to_json()
        resp = self.put(self._full_url(api_url), data=data)
        if not resp.ok:
            raise _make_api_error(resp.content)

        if resp.content:
            return ujson.loads(resp.content)
        return None

    def _post_codec(self, api_url, codec: Codec):
        """Send a POST request to the given URL.
        :param api_url: The /api/blah/blah to append to the base_url
        :param codec: A codec to convert to JSON and send
        :return: The JSON response as a dict, or None if none was sent
        """
        data = codec.to_json()
        resp = self.post(self._full_url(api_url), data=data)
        if not resp.ok:
            raise _make_api_error(resp.content)

        if resp.content:
            return ujson.loads(resp.content)
        return None

    def _post_raw(self, api_url, data: bytes, content_type: str):
        """Send a POST request to the given URL.
        :param api_url: The /api/blah/blah to append to the base url
        :param data: The raw data to send
        :param content_type: The mime type of the data being sent
        :return: The JSON response as a dict, or None of none was sent
        """
        resp = self.post(self._full_url(api_url),
                         data=data,
                         headers={'content-type': content_type})
        if not resp.ok:
            raise _make_api_error(resp.content)

        if resp.content:
            return ujson.loads(resp.content)
        return None

    def _post_json(self, api_url, json):
        """Send a POST request to the given URL.
        :param api_url: The /api/blah/blah to append to the base_url
        :param json: Preformatted JSON to send
        :return: The JSON response as a dict, or None if none was sent
        """
        resp = self.post(self._full_url(api_url), data=json)
        if not resp.ok:
            raise _make_api_error(resp.content)

        if resp.content:
            return ujson.loads(resp.content)
        return None

    def _put_json(self, api_url, json):
        """Send a PUT request to the given URL.
        :param api_url: The /api/blah/blah to append to the base_url
        :param json: Preformatted JSON to send
        :return: The JSON response as a dict, or None if none was sent
        """
        resp = self.put(self._full_url(api_url), data=json)
        if not resp.ok:
            raise _make_api_error(resp.content)

        if resp.content:
            return ujson.loads(resp.content)
        return None

    def _delete(self, api_url, params=None):
        """Sends a DELETE request to the given URL.
        :param api_url: The /api/blah/blah to append to the base_url
        :param params: The "query_string" to add to the URL. Must be a
          str-to-str dict
        :return: The JSON response as a dict, or None if none was sent
        """
        resp = self.delete(self._full_url(api_url), params=params)
        if not resp.ok:
            raise _make_api_error(resp.content)

        if resp.content:
            return ujson.loads(resp.content)
        return None

    def _full_url(self, api_url):
        url = "{base_url}{api_url}".format(
            base_url=self._server_url,
            api_url=api_url)
        return url


def _make_api_error(resp_content):
    """Makes the corresponding error for this response.

    :param resp_content: The HTTP response to inspect for info
    :return: An error that can be thrown describing this failure
    """
    if len(resp_content) == 0:
        kind = error_kinds.UNKNOWN
        description = ("A failure happened but the server did not respond "
                       "with a proper error")
    else:
        resp_content = ujson.loads(resp_content)
        kind = resp_content["title"]
        description = resp_content["description"]

    if kind not in api_errors.kind_to_error_type:
        logging.warning(f"Unknown error kind {kind}")
        return api_errors.UnknownError(description)
    else:
        return api_errors.kind_to_error_type[kind](description)
