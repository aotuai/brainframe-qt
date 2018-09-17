from brainframe.client.api.api_stub import API


class APIWrapper(API):
    """Wrapped API object so that QtDesigner can initialize without API
    instance

    If _server_url is not set, it assumes that it is being used from QtDesigner
    """

    def __getattribute__(self, item):
        """If __getattribute__ fails, this is called"""
        server_url = object.__getattribute__(self, "_server_url")
        if server_url or item == "set_url":
            return object.__getattribute__(self, item)
        if item == "get_stream_configurations":
            return object.__getattribute__(self, "_" + item)
        if item == "get_status_poller":
            return object.__getattribute__(self, "_" + item)
        return None

    @staticmethod
    def _get_stream_configurations():
        return []

    @staticmethod
    def _get_status_poller():
        return None


# API instance that is later monkeypatched to be a singleton
api: API = APIWrapper()
