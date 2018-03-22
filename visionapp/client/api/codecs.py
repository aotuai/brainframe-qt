import abc
import ujson


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
    """This holds logic information for a ZoneAlarm.
    """

    def __init__(self, *, test, check_value, with_class_name, attribute, id_=None):
        self.test = test
        self.check_value = check_value
        self.with_class_name = with_class_name
        self.with_attribute = attribute
        self.id = id_

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        d["with_attribute"] = self.with_attribute.to_dict()
        return d

    @staticmethod
    def from_dict(d: dict):
        return ZoneAlarmCondition(
            test=d["test"],
            check_value=d["check_value"],
            with_class_name=d["with_class_name"],
            attribute=Attribute.from_dict(d["with_attribute"]),
            id_=d["id"])


class ZoneAlarm(Codec):
    """This is the configuration for an alarm.
    """

    def __init__(self, *, name, conditions,
                 use_active_time, active_start_time, active_end_time, id_=None):
        self.name = name
        self.id = id_
        self.conditions = conditions
        self.use_active_time = use_active_time
        self.active_start_time = active_start_time
        self.active_end_time = active_end_time

    def to_dict(self):
        d = dict(self.__dict__)
        d["conditions"] = [ZoneAlarmCondition.to_dict(cond)
                           for cond in self.conditions]
        return d

    @staticmethod
    def from_dict(d):
        conditions = [ZoneAlarmCondition.from_dict(cond)
                      for cond in d["conditions"]]
        return ZoneAlarm(name=d["name"],
                         id_=d["id"],
                         conditions=conditions,
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

    def __init__(self, *, alarm_id, start_time, end_time, verified_as, id_=None):
        self.id = id_
        self.alarm_id = alarm_id
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
                     start_time=d["start_time"],
                     end_time=d["end_time"],
                     verified_as=d["verified_as"])


class Zone(Codec):
    """The definition for a zone. It is a non-convex polygon or a line.
    """

    def __init__(self, *, name, alarms, coords, id_=None):
        self.name = name
        self.id = id_
        self.alarms = alarms
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

        "ipcamera"
        parameters: {"url": "http://185.10.80.33:8082"}

        "file"
        parameters: {"filepath": "/home/usr/videos/my_vid.mp4"}
    """

    def __init__(self, *, name, connection_type, parameters, id_=None, is_active=None):
        self.name = name
        self.id = id_
        self.connection_type = connection_type
        self.parameters = parameters
        self.is_active = is_active

    def to_dict(self):
        d = dict(self.__dict__)
        return d

    @staticmethod
    def from_dict(d):
        return StreamConfiguration(name=d["name"],
                                   id_=d["id"],
                                   connection_type=d["connection_type"],
                                   parameters=d["parameters"],
                                   is_active=d["is_active"])


# Engine related stuff
class EngineConfiguration(Codec):
    """This is for telling the client the capabilities of the engine. This might
    include the total number of streams available, the types of detectable
    objects, the types of attributes that can be detected, etc.
    """

    def __init__(self, *, version, detectable, max_streams):
        self.version = version
        self.detectable = detectable
        self.max_streams = max_streams

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return EngineConfiguration(version=d["version"],
                                   detectable=d["detectable"],
                                   max_streams=d["max_streams"])