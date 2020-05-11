from brainframe.api.api_stub import API
from .streaming import StreamManager


class APIWrapper(API):
    """Wrapped API object so that QtDesigner can initialize without API
    instance

    If _server_url is not set, it assumes that it is being used from QtDesigner
    """
    def __init__(self):
        super().__init__()
        self._stream_manager = None

    def __getattribute__(self, item):
        """If __getattribute__ fails, this is called"""

        # Mock methods
        if item == "_empty_func":
            return object.__getattribute__(self, item)

        server_url = object.__getattribute__(self, "_server_url")

        # If the server url is set (or we're accessing it), return the real
        # attribute
        if server_url or item == "set_url":
            return object.__getattribute__(self, item)

        # Otherwise return an empty shell of a function. Everything below is
        # used somewhere in QtDesigner plugin, so it needs to be faked
        if item == "get_stream_configurations":
            return self._empty_func([])
        if item == "get_status_receiver":
            return self._empty_func(None)
        if item == "get_plugins":
            return self._empty_func([])
        if item == "get_identities":
            return self._empty_func([], 0)
        if item == "get_encodings":
            return self._empty_func([])
        if item == "get_encoding_class_names":
            return self._empty_func([])
        if item == "get_alerts":
            return self._empty_func([], 0)
        if item == "get_zone_alarms":
            return self._empty_func([])

        return None

    @staticmethod
    def _empty_func(*rets):
        def mock_func(*_args, **_kwargs):
            if len(rets) > 1:
                return rets
            else:
                return rets[0]

        return mock_func

    def get_stream_manager(self):
        """Returns a singleton StreamManager object"""
        # Lazily import streaming code to avoid OpenCV dependencies unless
        # necessary
        from brainframe.client.api_helpers.streaming import StreamManager

        if self._stream_manager is None:
            self._stream_manager = StreamManager(self.get_status_receiver())
        return self._stream_manager


# API instance that is later monkeypatched to be a singleton
api: API = APIWrapper()
