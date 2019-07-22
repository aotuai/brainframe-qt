from typing import Tuple, Any, Optional
import ujson
import requests
import logging

from brainframe.client.api import api_errors
from brainframe.shared import error_kinds
from brainframe.client.api.codecs import Codec


class Stub:
    """A base class for API stubs: Classes that provide methods which call the
    API to provide some functionality. Included are methods to make
    communicating with the API easier.
    """
    _server_url = None
    _credentials = None
    _session_id = None

    def set_url(self, url):
        self._server_url = url

    def set_credentials(self, credentials: Optional[Tuple[str, str]]):
        """Start authorizing requests with the given credentials for all future
        requests.

        :param credentials: The username and password in a tuple, or None to
            not use authorization on requests
        """
        self._credentials = credentials

        # Stop using the old session with outdated credentials
        self._session_id = None

    def _get_json(self, api_url, params=None) -> Tuple[Any, dict]:
        """Send a GET request to the given URL and parse the result as JSON.

        :param api_url: The /api/blah/blah to append to the base_url
        :param params: The "query_string" to add to the url. In the format
            of a dict, {"key": "value", ...} key and val must be a string
        :return: The response, parsed with JSON
        """
        data, headers = self._get(api_url, params=params)

        if data:
            return ujson.loads(data), headers
        return None, headers

    def _put_json(self, api_url, json):
        """Send a PUT request to the given URL.

        :param api_url: The /api/blah/blah to append to the base_url
        :param json: Pre-formatted JSON to send
        :return: The JSON response as a dict, or None if none was sent
        """
        data, headers = self._put(api_url,
                                  data=json,
                                  content_type="application/json")

        if data:
            return ujson.loads(data)
        return None

    def _post_codec(self, api_url, codec: Codec):
        """Send a POST request to the given URL.

        :param api_url: The /api/blah/blah to append to the base_url
        :param codec: A codec to convert to JSON and send
        :return: The JSON response as a dict, or None if none was sent
        """
        codec_data = codec.to_json()
        data, headers = self._post(api_url,
                                   data=codec_data.encode("utf-8"),
                                   content_type="application/json")

        if data:
            return ujson.loads(data)
        return None

    def _post_json(self, api_url, json):
        """Send a POST request to the given URL.
        :param api_url: The /api/blah/blah to append to the base_url
        :param json: Preformatted JSON to send
        :return: The JSON response as a dict, or None if none was sent
        """
        data, headers = self._post(api_url,
                                   data=json,
                                   content_type="application/json")

        if data:
            return ujson.loads(data)
        return None

    def _post_multipart(self, api_url, files):
        """Send a POST request to the given URL.
        :param api_url: The /api/blah/blah to append to the base_url
        :param files: A tuple in Requests format for a multipart body
        :return: The JSON response as a dict, or None if none was sent
        """
        data, headers = self._post(api_url, files=files)

        if data:
            return ujson.loads(data)
        return None

    def _get(self, api_url, params=None) -> Tuple[bytes, dict]:
        """Send a GET request to the given URL, managing authentication and
        error handling, if necessary.

        :param api_url: The /api/blah/blah to append to the base_url
        :param params: The "query_string" to add to the url. In the format
            of a dict, {"key": "value", ...} key and val must be a string
        :return: The raw bytes of the response and the response headers
        """
        request = requests.Request(
            method="GET",
            url=self._full_url(api_url),
            params=params)

        return self._send_authorized(request)

    def _put(self, api_url, data: bytes, content_type: str) \
            -> Tuple[bytes, dict]:
        """Send a PUT request to the given URL, managing authentication and
        error handling, if necessary.

        :param api_url: The /api/blah/blah to append to the base_url
        :param data: The data to send
        :param content_type: The content type of the data
        :return: The raw bytes of the response and the response headers
        """
        headers = None
        if content_type is not None:
            headers = {"content-type": content_type}

        request = requests.Request(
            method="PUT",
            url=self._full_url(api_url),
            data=data,
            headers=headers)

        return self._send_authorized(request)

    def _post(self, api_url,
              data: bytes = None,
              content_type: str = None,
              files=None) \
            -> Tuple[bytes, dict]:
        """Send a POST request to the given URL, managing authentication and
        error handling, if necessary.

        :param api_url: The /api/blah/blah to append to the base_url
        :param data: The data to send
        :param content_type: The content type of the data
        :return: The raw bytes of the response and the response headers
        """
        headers = None
        if content_type is not None:
            headers = {"content-type": content_type}

        request = requests.Request(
            method="POST",
            url=self._full_url(api_url),
            data=data,
            files=files,
            headers=headers)

        return self._send_authorized(request)

    def _delete(self, api_url, params=None) -> Tuple[bytes, dict]:
        """Sends a DELETE request to the given URL, managing authentication and
        handling errors, as necessary.

        :param api_url: The /api/blah/blah to append to the base_url
        :param params: The "query_string" to add to the URL. Must be a
          str-to-str dict
        :return: The response bytes and headers
        """
        request = requests.Request(
            method="DELETE",
            url=self._full_url(api_url),
            params=params)

        return self._send_authorized(request)

    def _full_url(self, api_url):
        """Converts an API URL path to a fully qualified URL.

        :param api_url: A URL path in the format /api/blah/blah
        :return: Full URL
        """
        url = "{base_url}{api_url}".format(
            base_url=self._server_url,
            api_url=api_url)
        return url

    def _send_authorized(self, request: requests.Request) \
            -> Tuple[bytes, dict]:
        """Sends the given request, using whatever authorization path that is
        necessary and raising any errors.

        :param request: The request to send
        :return: The body of the request, and all response headers
        """
        if self._credentials is None:
            # No credentials provided, send the request without any auth
            resp = self._send_no_auth(request)
        elif self._session_id is None:
            # Authenticate with username and password to get a new session ID
            resp = self._send_with_credentials(request)
        else:
            # Authenticate with the session ID
            resp = self._send_with_session_id(request)

        return resp.content, resp.headers

    def _send_no_auth(self, request: requests.Request) -> requests.Response:
        """Sends the given request with no authorization."""
        resp = self._send_request(request)
        if not resp.ok:
            raise _make_api_error(resp.content)

        return resp

    def _send_with_credentials(self, request: requests.Request) \
            -> requests.Response:
        """Sends the given request with HTTP Basic Authorization."""
        request.auth = self._credentials

        resp = self._send_request(request)
        if not resp.ok:
            raise _make_api_error(resp.content)

        if "session_id" in resp.cookies:
            # Update the session ID if we don't already have one
            self._session_id = resp.cookies["session_id"]

        return resp

    def _send_with_session_id(self, request: requests.Request) \
            -> requests.Response:
        """Sends the given request with the session ID."""
        request.cookies = {"session_id": self._session_id}

        try:
            resp = self._send_request(request)
            if not resp.ok:
                raise _make_api_error(resp.content)
        except api_errors.InvalidSessionError:
            # The session likely expired. Try again with the username and
            # password to fetch a new session
            request.cookies = None
            return self._send_with_credentials(request)

        return resp

    @staticmethod
    def _send_request(request: requests.Request) -> requests.Response:
        """Sends a request to the server. This method is mocked out in unit
        tests.

        :param request: The request to send
        :return: The response data
        """
        prepared = request.prepare()
        return requests.Session().send(prepared)


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
        info = f"Unknown error kind {kind}: " + description
        logging.error(info)
        return api_errors.UnknownError(info)
    else:
        return api_errors.kind_to_error_type[kind](description)
