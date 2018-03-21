import requests

from visionapp.client.api.data_structures import *


class API:
    _instance = None

    # For testing purposes
    get = staticmethod(requests.get)
    put = staticmethod(requests.put)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self._base_url = self.hostname + ":" + str(self.port)

    def close(self):
        """Close all threaded parts of the API and then close the API connection
        """

    # Stream Configuration Stuff
    def get_stream_configurations(self):
        """Get all StreamConfigurations that currently exist.
        :return: [StreamConfiguration, StreamConfiguration, ...]
        """
        req = "/api/streams/"
        data = self._get(req)
        configs = [StreamConfiguration.from_dict(d) for d in data]
        return configs

    def set_stream_configuration(self, stream_configuration):
        """Update an existing stream configuration or create a new one
        If creating a new one, the stream_configuration.id will be None
        :param stream_configuration: StreamConfiguration
        :return: StreamConfiguration, initialized with an ID
        """
        req = "/api/streams/"
        data = self._put_codec(req, stream_configuration)
        config = StreamConfiguration.from_dict(data)
        return config

    def delete_stream_configuration(self, stream_name):
        """

        :param stream_name:
        :return:
        """

    # Stream Specific stuff
    def start_analyzing(self, stream_id):
        pass

    def stop_analyzing(self, stream_id):
        pass

    def start_stream(self, stream_id):
        """Tell server to start a stream
        :param stream_id: The ID of the stream configuration to open.
        :return:The URL to connect to for the stream.
            cv2.VideoCapture(URL) must be compatible.
        """

    def end_stream(self, stream_id):
        """
        This tells BrainServer to close its socket for this stream
        :param stream_id:
        :return:
        """

    # Get Analysis
    def get_latest_zone_statuses(self):
        """Get all ZoneStatuses

        :return:
        {“stream_id1”: [ZoneStatus, ZoneStatus], “stream_id2”: [ZoneStatus]}
        """

    # Alerts
    def get_unverified_alerts(self, stream_id):
        """Gets all alerts that have not been verified or rejected

        :param stream_id:
        :return:
        """
        req = "/api/alerts/unverified".format(
            stream_id=stream_id)
        data = self._get(req, params={"stream_id": str(stream_id)})
        alerts = [Alert.from_dict(a) for a in data]
        return alerts

    def set_alert_verification(self, alert_id, verified_as: bool):
        """Sets an alert verified as True or False
        :param stream_id: The stream that the alert is part of
        :param alert_id: The
        :return: The modified Alert
        """
        req = "/api/alerts/{alert_id}".format(alert_id=alert_id)
        resp = self.put(self._full_url(req), data=ujson.dumps(verified_as))


    # Backend Capabilities
    def get_engine_configuration(self):
        """Returns the capabilities of the machine learning engine on the server.
        Currently, it can tell you:
            The types of objects that can be detected
            The types of attributes that can be detected for each object.

        :return: EngineConfiguration
        """

    # Zone specific stuff
    def get_zones(self, stream_id):
        """Returns a list of Zone's associated with that stream"""
        req = "/api/streams/{stream_id}/zones".format(stream_id=str(stream_id))
        data = self._get(req)
        zones = [Zone.from_dict(j) for j in data]
        return zones

    def get_zone(self, stream_id, zone_id):
        """Get a specific zone"""
        data = self.get_zones(stream_id)
        zones = [zone for zone in data if zone.id == zone_id]
        assert len(zones) != 0, ("A zone with that stream_id and zone_id could"
                                 " not be found!")
        return zones[0]

    def set_zone(self, stream_id, zone):
        """Update or create a zone. If the Zone doesn't exist, the zone.id
        must be None. An initialized Zone with an ID will be returned.
        :param stream_id: The stream_id that this zone exists in
        :param zone: A Zone object
        :return: Zone, initialized with an ID
        """
        req = "/api/streams/{stream_id}/zones".format(stream_id=stream_id)
        data = self._put_codec(req, zone)
        new_zone = Zone.from_dict(data)
        return new_zone

    def _get(self, api_url, params=None):
        """
        :param api_url: The /api/blah/blah to append to the base_url
        :param params: The "query_string" to add to the url. In the format
        of a dict, {"key": "value", ...} key and val must be a string
        :return:
        """
        response = self.get(self._full_url(api_url), params=params)
        return ujson.loads(response.content)

    def _put_codec(self, api_url, codec: Codec):
        data = codec.to_json()
        response = self.put(self._full_url(api_url), data=data)
        return ujson.loads(response.content)

    def _full_url(self, api_url):
        url = "{base_url}{api_url}".format(
            base_url=self._base_url,
            api_url=api_url)
        return url

if __name__ == "__main__":
    api = API("http://localhost", 8000)
    zones = api.get_zones(0)
    zone = api.get_zone(0, 2)

    new_zone = api.set_zone(0, zone)
    print(zone)
    print(zones)
    print(new_zone)
