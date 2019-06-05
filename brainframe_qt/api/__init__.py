from .api_stub import API


class APIWrapper(API):
    """Wrapped API object so that QtDesigner can initialize without API
    instance

    If _server_url is not set, it assumes that it is being used from QtDesigner
    """

    def __getattribute__(self, item):
        """If __getattribute__ fails, this is called"""
        server_url = object.__getattribute__(self, "_server_url")

        # If the server url is set (or we're accessing it), return the real
        # attribute
        if server_url or item == "set_url":
            return object.__getattribute__(self, item)

        # Otherwise return an empty shell of a function. Everything below is
        # used somewhere in QtDesigner plugin, so it needs to be faked
        if item == "get_stream_configurations":
            return lambda: []
        if item == "get_status_poller":
            return lambda: None
        if item == "get_plugins":
            return lambda: []
        if item == "get_identities":
            return lambda: []
        if item == "get_encodings":
            return lambda: []

        return None


# API instance that is later monkeypatched to be a singleton
api: API = APIWrapper()
