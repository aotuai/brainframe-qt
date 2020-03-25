from enum import Enum, auto
from typing import Callable, Dict, List, Union

from brainframe.client.api.codecs import Alert, StreamConfiguration, Zone, \
    ZoneAlarm

ZSSDatumType = Union[
    StreamConfiguration,
    Zone,
    ZoneAlarm,
    Alert
]

ZSSDataType = List[ZSSDatumType]


class ZSSTopic(Enum):
    STREAMS = auto()
    ZONES = auto()
    ALARMS = auto()
    ALERTS = auto()


class _Subscription:

    def __init__(self, callback: Callable, filters=None):
        self.callback: Callable = callback
        self.filters: Dict[str, int] = filters or {}

    def __repr__(self):
        return f"zss_pubsub.Subscription(" \
               f"{self.callback.__qualname__}, {self.filters}" \
               f")"

    def filter_data(self, datum: ZSSDatumType):
        if isinstance(datum, StreamConfiguration):
            return self._filter_stream(datum)
        elif isinstance(datum, Zone):
            return self._filter_zone(datum)
        elif isinstance(datum, ZoneAlarm):
            return self._filter_alarm(datum)
        elif isinstance(datum, Alert):
            return self._filter_alert(datum)

    # noinspection PyMethodMayBeStatic
    def _filter_stream(self, _stream: StreamConfiguration):
        # Currently there are no filters for streams
        return True

    def _filter_zone(self, zone: Zone):
        if self.filters["stream_id"] not in [any, zone.stream_id]:
            return False
        return True

    def _filter_alarm(self, alarm: ZoneAlarm):
        if self.filters["stream_id"] not in [any, alarm.stream_id]:
            return False
        if self.filters["zone_id"] not in [any, alarm.zone_id]:
            return False
        return True

    def _filter_alert(self, alert: Alert):
        # Currently unsupported
        # if self.filters["stream_id"] not in [any, alert.stream_id]:
        #     return False
        # if self.filters["zone_id"] not in [any, alert.zone_id]:
        #     return False
        if self.filters["alarm_id"] not in [any, alert.alarm_id]:
            return False
        return True


class _ZSSPubSub:

    def __init__(self):
        super().__init__()

        self.subscriptions: Dict[ZSSTopic, List[_Subscription]] = {
            ZSSTopic.STREAMS: [],
            ZSSTopic.ZONES: [],
            ZSSTopic.ALARMS: [],
            ZSSTopic.ALERTS: []
        }

    def publish(self, message: Dict[ZSSTopic, ZSSDataType]):
        for topic, data in message.items():

            subscribers = self.subscriptions[topic]

            for subscriber in subscribers:
                data_to_publish = list(filter(subscriber.filter_data, data))
                if len(data_to_publish) > 0:
                    subscriber.callback(data_to_publish)

    def subscribe(self, topic, callback: Callable, filters=None):
        self.subscriptions[topic].append(_Subscription(callback, filters))

    def subscribe_streams(self, callback: Callable):
        self.subscribe(ZSSTopic.STREAMS, callback)

    def subscribe_zones(self, callback: Callable, stream_id=any):

        filters = {"stream_id": stream_id}

        self.subscribe(ZSSTopic.ZONES, callback,
                       filters=filters)

    def subscribe_alarms(self, callback: Callable, stream_id=any, zone_id=any):

        filters = {"stream_id": stream_id,
                   "zone_id": zone_id}

        self.subscribe(ZSSTopic.ALARMS, callback,
                       filters=filters)

    def subscribe_alerts(self, callback: Callable,
                         stream_id=any, zone_id=any, alarm_id=any):

        filters = {"stream_id": stream_id,
                   "zone_id": zone_id,
                   "alarm_id": alarm_id}

        self.subscribe(ZSSTopic.ALERTS, callback,
                       filters=filters)


# noinspection SpellCheckingInspection
zss_publisher = _ZSSPubSub()
