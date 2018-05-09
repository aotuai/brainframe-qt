import abc
import ujson
from collections import Counter
from enum import Enum


class Codec(abc.ABC):
    @abc.abstractmethod
    def to_dict(self) -> dict:
        pass

    @staticmethod
    @abc.abstractmethod
    def from_dict(d: dict):
        pass

    def to_json(self) -> str:
        return ujson.dumps(self.to_dict())

    @classmethod
    def from_json(cls, j: str):
        return cls.from_dict(ujson.loads(j))

    def __repr__(self):
        return str(self.to_dict())


class Detection(Codec):
    """A detected object. It can have 'children', for example, a "person" can
    have a "face" object as a child. It can also own several Attributes. For
    example, a "person" can exhibit a behaviour. A Face can have a gender.
    """

    def __init__(self, *, class_name, rect, children, attributes):
        self.class_name = class_name
        self.rect = rect
        self.children = children
        self.attributes = attributes

    def to_dict(self):
        d = dict(self.__dict__)
        d["children"] = [Detection.to_dict(det) for det in self.children]
        d["attributes"] = [Attribute.to_dict(att) for att in self.attributes]
        return d

    @property
    def height(self):
        return self.rect[3] - self.rect[1]

    @property
    def width(self):
        return self.rect[2] - self.rect[0]

    @property
    def coords(self):
        """Conveniently return a list of coordinates, polygon style"""
        return [(self.rect[0], self.rect[1]),
                (self.rect[2], self.rect[1]),
                (self.rect[2], self.rect[3]),
                (self.rect[0], self.rect[3])]

    @staticmethod
    def from_dict(d):
        children = [Detection.from_dict(det) for det in d["children"]]
        attributes = [Attribute.from_dict(att) for att in d["attributes"]]
        return Detection(class_name=d["class_name"],
                         rect=d["rect"],
                         children=children,
                         attributes=attributes)


class Attribute(Codec):
    """This holds an attribute of a detection. These should _not_ be made
    on the client side
    """

    def __init__(self, *, category=None, value=None):
        self.category = category
        self.value = value

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Attribute(category=d["category"],
                         value=d["value"])


class ZoneAlarmCondition(Codec):
    """This holds logic information for a ZoneAlarm."""

    test_types = [">", "<", "=", "!="]

    def __init__(self, *, test, check_value, with_class_name, with_attribute,
                 id_=None):
        self.test = test
        self.check_value = check_value
        self.with_class_name = with_class_name
        self.with_attribute = with_attribute
        self.id = id_

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        if self.with_attribute is not None:
            d["with_attribute"] = self.with_attribute.to_dict()

        return d

    @staticmethod
    def from_dict(d: dict):
        # with_attribute is an optional parameter
        with_attribute = None
        if d["with_attribute"] is not None:
            with_attribute = Attribute.from_dict(d["with_attribute"])

        return ZoneAlarmCondition(
            test=d["test"],
            check_value=d["check_value"],
            with_class_name=d["with_class_name"],
            with_attribute=with_attribute,
            id_=d["id"])


class ZoneAlarmRateCondition(Codec):
    """A condition that must be met for an alarm to go off. Compares the rate of
    change in the count of some object against a test value.
    """

    test_types = [">=", "<="]

    # noinspection PyArgumentList
    # PyCharm incorrectly complains
    DirectionType = Enum("DirectionType",
                         ["entering", "exiting", "entering_or_exiting"])

    def __init__(self, *, test, duration, change, direction, with_class_name,
                 with_attribute, id_=None):
        self.test = test
        self.duration = duration
        self.change = change
        self.direction = direction
        self.with_class_name = with_class_name
        self.with_attribute = with_attribute
        self.id = id_

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        if self.with_attribute is not None:
            d["with_attribute"] = self.with_attribute.to_dict()

        d["direction"] = self.direction.name

        return d

    @staticmethod
    def from_dict(d: dict):
        # with_attribute is an optional parameter
        with_attribute = None
        if d["with_attribute"] is not None:
            with_attribute = Attribute.from_dict(d["with_attribute"])

        return ZoneAlarmRateCondition(
            test=d["test"],
            duration=d["duration"],
            change=d["change"],
            direction=ZoneAlarmRateCondition.DirectionType[d["direction"]],
            with_class_name=d["with_class_name"],
            with_attribute=with_attribute,
            id_=d["id"])


class ZoneAlarm(Codec):
    """This is the configuration for an alarm."""

    def __init__(self, *, name, count_conditions, rate_conditions,
                 use_active_time, active_start_time, active_end_time, id_=None):
        self.name = name
        self.id = id_
        self.count_conditions = count_conditions
        self.rate_conditions = rate_conditions
        self.use_active_time = use_active_time
        self.active_start_time = active_start_time
        self.active_end_time = active_end_time

    def to_dict(self):
        d = dict(self.__dict__)
        d["count_conditions"] = [ZoneAlarmCondition.to_dict(cond)
                                 for cond in self.count_conditions]
        d["rate_conditions"] = [ZoneAlarmRateCondition.to_dict(cond)
                                for cond in self.rate_conditions]

        return d

    @staticmethod
    def from_dict(d):
        count_conditions = [ZoneAlarmCondition.from_dict(cond)
                            for cond in d["count_conditions"]]
        rate_conditions = [ZoneAlarmRateCondition.from_dict(cond)
                           for cond in d["rate_conditions"]]

        return ZoneAlarm(name=d["name"],
                         id_=d["id"],
                         count_conditions=count_conditions,
                         rate_conditions=rate_conditions,
                         use_active_time=d["use_active_time"],
                         active_start_time=d["active_start_time"],
                         active_end_time=d["active_end_time"])


class Alert(Codec):
    """This is sent when an Alarm has been triggered.
    An alert can be sent WITHOUT an end_time, but never without a start_time.

    self.verified_as can be True, False or None.
        If True, then this alert was labeled by a person as being legitimate
        If False,then this alert was labeled by a person as being a false alarm
        If None, then this alert has not been labeled yet.
    """

    def __init__(self, *, alarm_id, zone_id, start_time, end_time, verified_as,
                 id_=None):
        self.id = id_
        self.alarm_id = alarm_id
        self.zone_id = zone_id
        self.start_time = start_time
        self.end_time = end_time
        self.verified_as = verified_as

    def to_dict(self):
        d = dict(self.__dict__)
        return d

    @staticmethod
    def from_dict(d):
        return Alert(id_=d["id"],
                     alarm_id=d["alarm_id"],
                     zone_id=d["zone_id"],
                     start_time=d["start_time"],
                     end_time=d["end_time"],
                     verified_as=d["verified_as"])


class Zone(Codec):
    """The definition for a zone. It is a non-convex polygon or a line.

    :param coords: List of lists (ex: [[0, 0], [10, 10], [100, 500], [0, 500]])
    points are pixel based, with (0, 0) at top left
    """

    def __init__(self, *, name, coords, stream_id, alarms=(), id_=None):
        self.name = name
        self.id = id_
        self.stream_id = stream_id
        self.alarms = list(alarms)
        self.coords = coords

    def to_dict(self):
        d = dict(self.__dict__)
        d["alarms"] = [alarm.to_dict() for alarm in self.alarms]
        return d

    @staticmethod
    def from_dict(d):
        alarms = [ZoneAlarm.from_dict(alarm_d) for alarm_d in d["alarms"]]
        return Zone(name=d["name"],
                    id_=d["id"],
                    alarms=alarms,
                    stream_id=d["stream_id"],
                    coords=d["coords"])


class ZoneStatus(Codec):
    """The current status of everything going on inside a zone.
    """

    def __init__(self, *, zone, tstamp, detections, alerts,
                 total_entered, total_exited):
        self.zone = zone
        self.tstamp = tstamp
        self.total_entered = total_entered
        self.total_exited = total_exited
        self.detections = detections
        self.alerts = alerts

    @property
    def detection_counts(self):
        """The current count of each class type detected in the video
        :returns: {'class_name': int count, ...} """
        counter = Counter([det.class_name for det in self.detections])
        return counter

    def to_dict(self):
        d = dict(self.__dict__)
        d["zone"] = self.zone.to_dict()
        d["detections"] = [det.to_dict() for det in self.detections]
        d["alerts"] = [alert.to_dict() for alert in self.alerts]
        return d

    @staticmethod
    def from_dict(d):
        zone = Zone.from_dict(d["zone"])
        detections = [Detection.from_dict(det) for det in d["detections"]]
        alerts = [Alert.from_dict(alert) for alert in d["alerts"]]
        return ZoneStatus(zone=zone,
                          tstamp=d["tstamp"],
                          total_entered=d["total_entered"],
                          total_exited=d["total_exited"],
                          detections=detections,
                          alerts=alerts)


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


class Identity(Codec):
    """A specific, recognizable object or person."""

    def __init__(self, *, id_, name, class_name, metadata):
        self.id = id_
        """A unique identifier."""

        self.name = name
        """The name of the identified detection."""

        self.class_name = class_name
        """The name of the class that this detection is of."""

        self.metadata = metadata
        """Any additional user-defined information about the identity."""

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Identity(
            id_=d["id"],
            name=d["name"],
            class_name=d["class_name"],
            metadata=d["metadata"])
