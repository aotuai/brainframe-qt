


class API:
    def __init__(self, hostname, port):
        pass

    def close(self):
        """Close all threaded parts of the API and then close the API connection
        """



# Stream Configuration Stuff
def get_stream_configurations():
    """Get all StreamConfigurations that currently exist.
    :return: [StreamConfiguration, StreamConfiguration, ...]
    """


def update_stream_configuration(stream_configuration):
    """Update an existing stream configuration
    :param stream_configuration: StreamConfiguration
    :return:
    """

def add_stream_configuration(name, config):
    """
    This tells BrainServer to save a new stream configuration.
    :param name: Name of the stream location
    :param config:
    :return: StreamConfiguration, with the new ID assigned by BrainServer
    """

def delete_stream_configuration(stream_name):
    """

    :param stream_name:
    :return:
    """

# Stream Specific stuff
def start_stream(stream_id):
    """Tell server to start a stream

    :param stream_id:
    :return:
    """

def end_stream(stream_id):
    """
    This tells BrainServer to close its socket for this stream
    :param stream_id:
    :return:
    """


def get_latest_zone_statuses():
    """Get all ZoneStatuses

    :return:
    {“stream_id1”: [ZoneStatus, ZoneStatus], “stream_id2”: [ZoneStatus]}
    """

def get_unverified_alerts(stream_id):
    """Gets all alerts that have not been verified or rejected

    :param stream_id:
    :return:
    """

def get_engine_configuration():
    """Returns the capabilities of the machine learning engine on the server.
    Currently, it can tell you:
        The types of objects that can be detected
        The types of attributes that can be detected for each object.

    :return: EngineConfiguration
    """

def set_zone(zone, stream_id):
    """Check if zone.name already exists, and create it if not.

    :param zone:
    :param stream_id:
    :return:
    """

def get_zones(stream_id):
    """Returns a list of all zones associated with that stream

    :param stream_id:
    :return:
    """

def get_zone(stream_id, zone_name):
    """

    :param stream_id:
    :param zone_name:
    :return:
    """



