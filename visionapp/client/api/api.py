import requests

from api.data_structures import *


class API:
    _instance = None

    # For testing purposes
    get = requests.get
    put = requests.put

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
        If creating a new one, the stream_configuration.id_ will be None
        :param stream_configuration: StreamConfiguration
        :return: StreamConfiguration, initialized with an ID
        """
        req = "/api/streams/"
        data = self._put(req, stream_configuration)
        config = StreamConfiguration.from_dict(data)
        return config

    def delete_stream_configuration(self, stream_name):
        """

        :param stream_name:
        :return:
        """

    # Stream Specific stuff
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

    def get_stream_timestamp(self, stream_id):
        """Get the current timestamp of the stream, from the server side.
        :returns: A Unix style timestamp for the stream"""

    # Get Analysis
    def get_latest_zone_statuses(self):
        """Get all ZoneStatuses

        :return:
        {“stream_id1”: [ZoneStatus, ZoneStatus], “stream_id2”: [ZoneStatus]}
        """

    def get_unverified_alerts(self, stream_id):
        """Gets all alerts that have not been verified or rejected

        :param stream_id:
        :return:
        """

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
        """Returns a list of Zone's associated with that stream
        :param zone_name: If zone_name is specified, only that zone will
            be returned by this function
        :param stream_id:
        :return:
        """
        req = "/api/streams/{stream_id}/zones".format(stream_id=str(stream_id))
        data = self._get(req)
        zones = [Zone.from_dict(j) for j in data]
        return zones

    def get_zone(self, stream_id, zone_id):
        req = "/api/streams/{stream_id}/zones/{zone_id}".format(
            stream_id=stream_id,
            zone_id=zone_id)
        data = self._get(req)
        zone = Zone.from_dict(data)
        return zone

    def set_zone(self, stream_id, zone: Zone):
        """Update or create a zone. If the Zone doesn't exist, the zone.id_
        must be None. An initialized Zone with an ID will be returned.
        :param zone: A Zone object
        :return: Zone, initialized with an ID
        """
        req = "/api/streams/{stream_id}/zones".format(stream_id=stream_id)
        data = self._put(req, zone)
        new_zone = Zone.from_dict(data)
        return new_zone

    def _get(self, api_url):
        url = "{base_url}{api_url}".format(
            base_url=self._base_url,
            api_url=api_url)

        response = self.get(url)
        return ujson.loads(response.content)

    def _put(self, api_url, codec: Codec):
        url = "{base_url}{api_url}".format(
            base_url=self._base_url,
            api_url=api_url)
        data = codec.to_json()
        response = self.put(url, data=data)
        return ujson.loads(response.content)


if __name__ == "__main__":
    api = API("http://localhost", 8000)
    zones = api.get_zones(0)
    zone = api.get_zone(0, 2)

    new_zone = api.set_zone(0, zone)
    print(zone)
    print(zones)
    print(new_zone)
