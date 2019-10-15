from collections import Counter
from typing import List, Optional, Dict

from .base_codecs import Codec
from .alarm_codecs import Alert, ZoneAlarm
from .detection_codecs import Detection


class Zone(Codec):
    """The definition for a zone. It is a non-convex polygon or a line.

    :param coords: List of lists (ex: [[0, 0], [10, 10], [100, 500], [0, 500]])
    points are pixel based, with (0, 0) at top left
    """

    def __init__(self, *, name, coords, stream_id, alarms=(), id_=None):
        self.name = name
        self.id = id_
        self.stream_id = stream_id
        self.alarms: List[ZoneAlarm] = list(alarms)
        self.coords = coords

    def get_alarm(self, alarm_id) -> Optional[ZoneAlarm]:
        for alarm in self.alarms:
            if alarm.id == alarm_id:
                return alarm
        return None

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

    def __init__(self, *, zone, tstamp, within, entering, exiting, alerts,
                 total_entered, total_exited):
        self.zone: Zone = zone
        self.tstamp: float = tstamp
        self.total_entered: dict = total_entered
        self.total_exited: dict = total_exited
        self.within: List[Detection] = within
        self.entering: List[Detection] = entering
        self.exiting: List[Detection] = exiting
        self.alerts: List[Alert] = alerts

    @property
    def detection_within_counts(self) -> dict:
        """The current count of each class type detected in the video
        :returns: {'class_name': int count, ...} """
        counter = Counter([det.class_name for det in self.within])
        return counter

    def to_dict(self):
        d = dict(self.__dict__)
        d["zone"] = self.zone.to_dict()
        d["within"] = [det.to_dict() for det in self.within]
        d["entering"] = [det.to_dict() for det in self.entering]
        d["exiting"] = [det.to_dict() for det in self.exiting]
        d["alerts"] = [alert.to_dict() for alert in self.alerts]
        return d

    @staticmethod
    def from_dict(d):
        zone = Zone.from_dict(d["zone"])
        within = [Detection.from_dict(det) for det in d["within"]]
        entering = [Detection.from_dict(det) for det in d["entering"]]
        exiting = [Detection.from_dict(det) for det in d["exiting"]]
        alerts = [Alert.from_dict(alert) for alert in d["alerts"]]
        return ZoneStatus(zone=zone,
                          tstamp=d["tstamp"],
                          total_entered=d["total_entered"],
                          total_exited=d["total_exited"],
                          within=within,
                          entering=entering,
                          exiting=exiting,
                          alerts=alerts)
