from .base_codecs import Codec
from .condition_codecs import ZoneAlarmCondition, ZoneAlarmRateCondition


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
