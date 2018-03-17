import abc
import ujson


class Codec(abc.ABC):

    @abc.abstractmethod
    def to_dict(self) -> dict:
        pass

    @abc.abstractstaticmethod
    def from_dict(d: dict):
        pass


    def to_json(self) -> str:
        return ujson.dumps(self.to_dict())

    @classmethod
    def from_json(cls, j: str):
        return cls.from_dict(ujson.loads(j))


class Detection(Codec):
    """
    {"class_name": str "person" or "object name here",
    "rect": [x1, y1, x2, y2],

    # Child detections, like "face" or "feet" if this Detection was "person"
    "children": [Detection, Detection]

    # Attributes directly relevant to "person"
    "attributes":  [Attribute, Attribute, Attribute]
    }
    """
    def __init__(self, *, class_name, rect, children, attributes):
        self.class_name = class_name
        self.rect = rect
        self.children = children
        self.attributes = attributes


    def to_dict(self):
        d = self.__dict__
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
    """
    {
    "category": "Gender",
    "value": "male"
    }
    """
    def __init__(self, *, category, value):
        self.category = category
        self.value = value

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Attribute(category=d["category"],
                         value=d["value"])


"""
Make:
- Attribute class
    name: "boy"
    category: "gender"
    
ZoneAlarmCondition
    - Take conditional elements
    
"""



class ZoneAlarmCondition(Codec):
    """
    {
    "test": >, <, =, !=
    "check_value": integer
    "with_class_name": "person"
    "attribute": Attribute object
    }
    """
    def __init__(self, *, test, check_value, with_class_name, attribute):
        self.test = test
        self.check_value = check_value
        self.with_class_name = with_class_name
        self.with_attribute = attribute

    def to_dict(self) -> dict:
        d = self.__dict__
        d["with_attribute"] = self.with_attribute.to_dict()
        return d

    @staticmethod
    def from_dict(d: dict):
        return ZoneAlarmCondition(
            test=d["test"],
            check_value=d["check_value"],
            with_class_name=d["with_class_name"],
            attribute=Attribute.from_dict(d["with_attribute"]))


class ZoneAlarm(Codec):
    """
    {
    "id": int,
    "name": str,
    "conditions": [ZoneAlarmCondition, ZoneAlarmCondition]
    "use_active_time": bool,
    "start_time":  "HH:MM:SS" using 24 hour time,
    "end_time": "HH:MM:SS" using 24 hour time}
    """

    def __init__(self, *, name, conditions,
                 use_active_time, active_time_start, active_time_end, id_=None):
        self.name = name
        self.id_ = id_
        self.conditions = conditions
        self.use_active_time = use_active_time
        self.active_time_start = active_time_start
        self.active_time_end = active_time_end



    def to_dict(self):
        d = self.__dict__
        d["id"] = d.pop("id_")
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
                         active_time_start=d["active_time_start"],
                         active_time_end=d["active_time_end"])


class Alert(Codec):
    """
    An alert can be sent WITHOUT an end_time, but never without a start_time.
    The data will ONLY record alerts that have finished.
    {"id": int,
    "alarm_id": the id for this alerts alarm,
    "start_time": ms,
    "end_time": None or ms
    }
    """

    def __init__(self, *, alarm_id, start_time, end_time, id_=None):
        self.id_ = id_
        self.alarm_id = alarm_id
        self.start_time = start_time
        self.end_time = end_time

    def to_dict(self):
        d = self.__dict__
        d["id"] = d.pop("id_")
        return d

    @staticmethod
    def from_dict(d):
        return Alert(id_=d["id"],
                     alarm_id=d["alarm_id"],
                     start_time=d["start_time"],
                     end_time=d["end_time"])


class Zone(Codec):
    """
    {"name": str,
    "id": int,
    "stream_id": the stream id that this zone belongs to,
    "alarms": [Alarm, Alarm, Alarm]
    "coords": [[x1, y1], [x2, y2], [x3, y3], [x4, y4] ... [xn, yn]]
    """

    def __init__(self, *, name, alarms, coords, id_=None):
        self.name = name
        self.id_ = id_
        self.alarms = alarms
        self.coords = coords

    def to_dict(self):
        d = self.__dict__
        alarms = [alarm.to_dict() for alarm in self.alarms]
        d["id"] = d.pop("id_")
        d["alarms"] = alarms
        return d

    @staticmethod
    def from_dict(d):
        alarms = [ZoneAlarm.from_dict(alarm_d) for alarm_d in d["alarms"]]
        return Zone(name=d["name"],
                    id_=d["id"],
                    alarms=alarms,
                    coords=d["coords"])


class ZoneStatus(Codec):
    """
    {"zone": Zone,
     "tstamp": ms,
     "total_count": {"person": 100, "dog": 5},
     "detections": [Detection, Detection, Detection, Detection]
     "alerts": [Alert, Alert]
     }
    """

    def __init__(self, *, zone, tstamp, total_counts, detections, alerts):
        self.zone = zone
        self.tstamp = tstamp
        self.total_counts = total_counts
        self.detections = detections
        self.alerts = alerts

    def to_dict(self):
        d = self.__dict__
        d["zone"] = self.zone.to_dict()
        d["detections"] = [det.to_dict() for det in self.detections]
        # d["detections"] = {class_name: [det.to_dict() for det in dets]
        #                    for class_name, dets in self.detections.items()}
        d["alerts"] = [alert.to_dict() for alert in self.alerts]
        return d

    @staticmethod
    def from_dict(d):
        zone = Zone.from_dict(d["zone"])
        detections = [Detection.from_dict(det) for det in d["detections"]]
        # detections = {class_name: [Detection.from_dict(det) for det in dets]
        #               for class_name, dets in d["detections"].items()}
        alerts = [Alert.from_dict(alert) for alert in d["alerts"]]
        return ZoneStatus(zone=zone,
                          tstamp=d["tstamp"],
                          total_counts=d["total_counts"],
                          detections=detections,
                          alerts=alerts)


# Stream Data structures
class StreamConfiguration(Codec):
    """
    A stream configuration can only be gotten from the API, and has an
    ID.
    {"name": str,
    "id": int,
    "connection_type": "Webcam" or "IPPassword"
    "parameters": The JSON defining the parameters for this connection type

    Parameters
    "Webcam"
        {"device_index": int}

    "IPPassword"
        {"url": valid URL, "username": str, "password": str}
    }
    """

    def __init__(self, *, name, connection_type, parameters, id_=None):
        self.name = name
        self.id_ = id_
        self.connection_type = connection_type
        self.parameters = parameters


    def to_dict(self):
        d = self.__dict__
        d["id"] = d.pop("id_")
        return d

    @staticmethod
    def from_dict(d):
        # Get the config
        return StreamConfiguration(name=d["name"],
                                   id_=d["id"],
                                   connection_type=d["connection_type"],
                                   parameters=d["parameters"])


# Engine related stuff
class EngineConfiguration(Codec):
    """This is for telling the client the capabilities of the engine. This might
    include the total number of streams available, the types of detectable
    objects, the types of attributes that can be detected, etc.

    {"version": "0.0.0.1",
    "detectable": {"CLASS_NAME": {"ATTRIBUTE_TYPE": ["OPTION1", "OPTIONS2"]},
                   "person": {"gender": ["boy", "girl"],
                              "basic_behaviour": ["drinking_water", "smoking", "phoning"],
                              "posture": ["standing", "sitting", "lying_down"]
                              }
                   },
    "max_streams": 4 # License restrictions}
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


