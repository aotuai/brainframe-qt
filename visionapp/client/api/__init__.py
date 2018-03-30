from visionapp.client.api.api_stub import API, APIError


class _MockAPI:
    """Mock API object so that QtDesigner can initialize without API instance"""

    def __getattr__(self, item):
        """If __getattribute__ fails, this is called"""
        return None

    @staticmethod
    def get_stream_configurations():
        return []

    @staticmethod
    def get_status_poller():
        return None

# API instance that is later monkeypatched to be a singleton
# TODO: Use Py3.6 variable annotations when available
api = _MockAPI()  # type: API
