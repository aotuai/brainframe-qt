from visionapp.client.api.api_stub import API, APIError

# API instance that is later monkeypatched to be a singleton
api = None  # type: API  # TODO: Use Py3.6 variable annotations when available
