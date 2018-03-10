import abc


class Dictable(abc.ABC):
    @abc.abstractstaticmethod
    def from_dict(d):
        pass

    @abc.abstractmethod
    def to_dict(self):
        pass


class Detection(Dictable):
    """
    {"class_name": str "person" or "object name here",
    "rect": [x1, y1, x2, y2],
    "attributes": ["boy", "drinking_water"]}
    """

    def __init__(self, class_name, rect, attributes):
        self.class_name = class_name
        self.rect = rect
        self.attributes = attributes

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Detection(class_name=d["class_name"],
                         rect=d["rect"],
                         attributes=d["attributes"])


class Alarm(Dictable):
    """
    {"name": str,
    "id": int,
    "with_class_name": The class name of detected object in order to be counted
    "with_attributes": the attribute for a person to have to be counted,
    "check_value": The int value or threshhold to be over, under, or equal to,
    "tests": >, <, !=, == (as string),
    "use_active_time": bool,
    "start_time":  "HH:MM" using 24 hour time,
    "end_time": "HH:MM" using 24 hour time}
    """

    def __init__(self, name, id_, test, check_value,
                 with_class_name, with_attributes,
                 use_active_time, active_time_start, active_time_end):
        self.name = name
        self.id_ = id_
        self.test = test
        self.check_value = check_value
        self.with_class_name = with_class_name
        self.with_attributes = with_attributes
        self.use_active_time = use_active_time
        self.active_time_start = active_time_start
        self.active_time_end = active_time_end

    def to_dict(self):
        d = self.__dict__
        d["id"] = d.pop("id_")
        return d

    @staticmethod
    def from_dict(d):
        return Alarm(name=d["name"],
                     id_=d["id"],
                     test=d["tests"],
                     check_value=d["check_value"],
                     with_class_name=d["with_class_name"],
                     with_attributes=d["with_attributes"],
                     use_active_time=d["use_active_time"],
                     active_time_start=d["active_time_start"],
                     active_time_end=d["active_time_end"])


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

    def __init__(self, id_, alarm_id, start_time, end_time):
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


class Zone(Dictable):
    """
    {"name": str,
    "id": int,
    "alarms": [Alarm, Alarm, Alarm]
    "coords": [[x1, y1], [x2, y2], [x3, y3], [x4, y4] ... [xn, yn]]
    """

    def __init__(self, name, id_, alarms, coords):
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
        alarms = [Alarm.from_dict(alarm_d) for alarm_d in d["alarms"]]
        return Zone(name=d["name"],
                    id_=d["id"],
                    alarms=alarms,
                    coords=d["coords"])


class ZoneStatus(Dictable):
    """
    {"zone": Zone,
     "tstamp": ms,
     "total_counts": {"person": 100, "dog": 5},
     "detections": {"person": [Detection, Detection], "dog": [Detection]}
     "alerts": [Alert, Alert]
     }
    """

    def __init__(self, zone, tstamp, total_counts, detections, alerts):
        self.zone = zone
        self.tstamp = tstamp
        self.total_counts = total_counts
        self.detections = detections
        self.alerts = alerts

    def to_dict(self):
        d = self.__dict__
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
                          total_counts=d["total_counts"],
                          detections=detections,
                          alerts=alerts)


# Stream Data structures
class WebcamConfig(Dictable):
    """
    {"device_index": int}
    """
    CONN_TYPE = "Webcam"

    def __init__(self, device_index):
        self.device_index = device_index

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return WebcamConfig(device_index=d["device_index"])

class IPPasswordConfig(Dictable):
    """
    {"url": valid URL, "username": str, "password": str}
    """
    CONN_TYPE = "IPPassword"

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return IPPasswordConfig(url=d["url"],
                                username=d["username"],
                                password=d["password"])

class StreamConfiguration(Dictable):
    """
    A stream configuration can only be gotten from the API, and has an
    ID.
    {"name": str,
    "id": int,
    "connection_type": "Webcam" or "IPPassword"
    "config": A serialized configuration
    }
    """
    CONN_TYPES = {WebcamConfig.CONN_TYPE: WebcamConfig,
                  IPPasswordConfig.CONN_TYPE: IPPasswordConfig}

    def __init__(self, name, id_, connection_type, config):
        self.name = name
        self.id_ = id_
        self.connection_type = connection_type
        self.config = config


    def to_dict(self):
        d = self.__dict__
        d["id"] = d.pop("id_")
        d["config"] = self.config.to_dict()
        return d

    @staticmethod
    def from_dict(d):
        # Get the config
        config_type = StreamConfiguration.CONN_TYPES[d["connection_type"]]
        config = config_type.from_dict(d["config"])
        return StreamConfiguration(name=d["name"],
                                   id_=d["id"],
                                   connection_type=d["connection_type"],
                                   config=config)



