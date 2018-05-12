from enum import Enum

from .base_codecs import Codec


# Stream Data structures
class StreamConfiguration(Codec):
    """Configuration for the server to open a video stream.

    Connection Types:
        "webcam"
        parameters: {"device_id": 0}

        "ip_camera"
        parameters: {"url": "http://185.10.80.33:8082"}

        "file"
        parameters: {"filepath": "/home/usr/videos/my_vid.mp4"}
    """
    # noinspection PyArgumentList
    # PyCharm incorrectly complains
    ConnType = Enum("ConnType",
                    ["ip_camera", "webcam", "file"])

    def __init__(self, *, name, connection_type, parameters, id_=None):
        assert connection_type in StreamConfiguration.ConnType, \
            "You must feed StreamConfiguration.ConnType into connection_type" \
            " You used a " + str(type(connection_type)) + " instead!"

        self.name = name
        self.id = id_
        self.connection_type = connection_type
        self.parameters = parameters

    def to_dict(self):
        d = dict(self.__dict__)
        d["connection_type"] = self.connection_type.name
        return d

    @staticmethod
    def from_dict(d):
        connection_t = StreamConfiguration.ConnType[d["connection_type"]]
        return StreamConfiguration(name=d["name"],
                                   id_=d["id"],
                                   connection_type=connection_t,
                                   parameters=d["parameters"])


# Engine related stuff
class EngineConfiguration(Codec):
    """This is for telling the client the capabilities of the engine. This
    might include the total number of streams available, the types of
    detectable objects, the types of attributes that can be detected, etc.
    """

    def __init__(self, *, version, attribute_ownership, attributes,
                 max_streams):
        self.version = version

        self.attribute_ownership = attribute_ownership
        """Attribute types (categories) supported by each detection class in the
        network

        A dict where the key is a detection class and the value is a list of
        all attribute types that may apply to that detection class. The value
        is not the same as the dict returned by EngineConfiguration.attributes
        so that multiple detection classes can share the same attributes

        Ex: {'person': ['Behavior', 'Gender']}
        """

        self.attributes = attributes
        """Possible values for each detection class

        A dict where the key is an attribute type (category) and the value is a
        list of possible values for the attribute type.

        Ex: {'Behavior': ['drinking', 'phoning', 'smoking', 'unknown']}
        """

        self.max_streams = max_streams
        """The maximum amount of allowed streams that can have analysis run on
        them at once"""

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return EngineConfiguration(
            version=d["version"],
            attributes=d["attributes"],
            attribute_ownership=d["attribute_ownership"],
            max_streams=d["max_streams"])
