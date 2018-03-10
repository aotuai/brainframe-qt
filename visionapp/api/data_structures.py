import abc


class Dictable(abc.ABC):

    @abc.abstractstaticmethod
    def from_dict(d):
        pass

    @abc.abstractmethod
    def to_dict(self, d):
        pass


class ZoneStatus(Dictable):
    """
    {"zone": Zone,
     "tstamp": ms,
     "total_count": {"person": 100, "dog": 5},
     "objects": {"person": [Detection, Detection], "dog": [Detection]}
     "alerts": [Alert, Alert]
     }
    """
    def to_dict(self, d):
        pass

    def __init__(self, zone, tstamp, total_count, objects, alerts):
        pass

    @staticmethod
    def from_dict(d):
        zone = Zone.from_dict(j["zone"])
        tstamp = j['tstamp']
        total_count = j['total_count']
        objects = [Detection.from_dict(det) for det in j["objects"]]
        alerts = [Alert.from_dict(alert) for alert in j["alerts"]]
        return ZoneStatus(zone, tstamp, total_count, objects, alerts)


class Zone(Dictable):
    """
    {"name": str,
    "id": int,
    "alarms": [Alarm, Alarm, Alarm]
    "coords": [[x1, y1], [x2, y2], [x3, y3], [x4, y4] ... [xn, yn]]
    """

    def to_dict(self, d):
        pass

    @staticmethod
    def from_dict(d):
        pass


class Detection(Dictable):
    """
    {"class_name": str "person" or "object name here",
    "rect": [x1, y1, x2, y2],
    "attributes": ["boy", "drinking_water"]}
    """
    def to_dict(self, d):
        pass

    @staticmethod
    def from_dict(d):
        pass


class Alarm(Dictable):
    """
    {"name": str,
    "id": int,
    "with_class_name": The class name of detected object in order to be counted
    "with_attributes": the attribute for a person to have to be counted,
    "check_value": The int value or threshhold to be over, under, or equal to,
    "test": >, <, !=, == (as string),
    "use_active_time": bool,
    "active_time_start":  "HH:MM" using 24 hour time,
    "active_time_end": "HH:MM" using 24 hour time}
    """
    def to_dict(self, d):
        pass

    @staticmethod
    def from_dict(d):
        pass


class Alert(Dictable):
    """
    An alert can be sent WITHOUT an end_time, but never without a start_time.
    The database will ONLY record alerts that have finished.
    {"id": int,
    "alarm_id": the id for this alerts alarm,
    "start_time": ms,
    "end_time": None or ms
    }
    """


# Stream Data structures
class StreamConfiguration(Dictable):
    """
    A stream configuration can only be gotten from the API, and has an
    ID.
    {"name": str, "id": int, "config": Some camera config object}
    """

    def to_dict(self, d):
        pass

    @staticmethod
    def from_dict(d):
        pass


class WebcamConfig(Dictable):
    """
    {"device_index": int}
    """
    CONN_TYPE = "Webcam"

    def to_dict(self, d):
        pass

    @staticmethod
    def from_dict(d):
        pass


class IPPasswordConfig(Dictable):
    """
    {"url": valid URL, "username": str, "password": str}
    """
    TYPE = "IPPassword"

    def to_dict(self, d):
        pass

    @staticmethod
    def from_dict(d):
        pass









