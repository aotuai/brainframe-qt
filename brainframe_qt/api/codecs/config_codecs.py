from typing import Optional

from .base_codecs import Codec
from brainframe.shared import codec_enums


# Stream Data structures
class StreamConfiguration(Codec):
    """Configuration for the server to open a video stream.

    Connection Types:
        "webcam"
        connection_options: {"device_id": 0}

        "ip_camera"
        connection_options: {"url": "http://185.10.80.33:8082"}

        "file"
        connection_options: {"filepath": "/home/usr/videos/my_vid.mp4"}
    """

    ConnType = codec_enums.ConnType

    def __init__(self, *, name: str,
                 connection_type: ConnType,
                 connection_options: dict,
                 runtime_options: dict,
                 premises_id: Optional[int],
                 id_=None):
        assert connection_type in StreamConfiguration.ConnType, \
            "You must feed StreamConfiguration.ConnType into connection_type" \
            " You used a " + str(type(connection_type)) + " instead!"

        self.name = name
        self.premises_id = premises_id
        self.id = id_
        self.connection_type = connection_type
        self.connection_options = connection_options
        self.runtime_options = runtime_options

    def to_dict(self):
        d = dict(self.__dict__)
        d["connection_type"] = self.connection_type.value
        return d

    @staticmethod
    def from_dict(d):
        connection_t = StreamConfiguration.ConnType(d["connection_type"])
        return StreamConfiguration(name=d["name"],
                                   id_=d["id"],
                                   connection_type=connection_t,
                                   connection_options=d["connection_options"],
                                   runtime_options=d["runtime_options"],
                                   premises_id=d["premises_id"])
