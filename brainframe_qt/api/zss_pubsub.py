import logging
from enum import Enum, auto
from threading import RLock
from typing import Callable, Dict, List, Set, Union

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


class Subscription:

    def __init__(self, topic: ZSSTopic, callback: Callable, filters=None):
        self.topic: ZSSTopic = topic
        self.callback: Callable = callback
        self.filters: Dict[str, int] = filters or {}

    def __repr__(self):
        return f"zss_pubsub.Subscription(" \
               f"{self.topic}, {self.callback.__qualname__}, {self.filters}" \
               f")"

    def filter_data(self, datum: ZSSDatumType):
        if self.topic is ZSSTopic.STREAMS:
            return self._filter_stream(datum)
        if self.topic is ZSSTopic.ZONES:
            return self._filter_zone(datum)
        if self.topic is ZSSTopic.ALARMS:
            return self._filter_alarm(datum)
        if self.topic is ZSSTopic.ALERTS:
            return self._filter_alert(datum)

    def _filter_stream(self, stream: StreamConfiguration):
        if self.filters["stream_id"] not in [any, stream.id]:
            return False
        return True

    def _filter_zone(self, zone: Zone):
        if self.filters["stream_id"] not in [any, zone.stream_id]:
            return False
        if self.filters["zone_id"] not in [any, zone.id]:
            return False
        return True

    def _filter_alarm(self, alarm: ZoneAlarm):
        if self.filters["stream_id"] not in [any, alarm.stream_id]:
            return False
        if self.filters["zone_id"] not in [any, alarm.zone_id]:
            return False
        if self.filters["alarm_id"] not in [any, alarm.id]:
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
        if self.filters["alert_id"] not in [any, alert.id]:
            return False
        return True


class _ZSSPubSub:

    def __init__(self):
        super().__init__()

        self.subscriptions_lock = RLock()
        self.subscriptions: Dict[ZSSTopic, Set[Subscription]] = {
            ZSSTopic.STREAMS: set(),
            ZSSTopic.ZONES: set(),
            ZSSTopic.ALARMS: set(),
            ZSSTopic.ALERTS: set()
        }

    def publish(self, message: Dict[ZSSTopic, ZSSDataType]):
        for topic, data in message.items():

            # We have the chance to modify the subscriptions while iterating
            # (even with the lock), so I just make a copy
            subscribers = list(self.subscriptions[topic])

            with self.subscriptions_lock:
                for subscriber in subscribers:
                    publish_data = list(filter(subscriber.filter_data, data))

                    try:
                        subscriber.callback(publish_data)
                    except RuntimeError as exc:
                        if "has been deleted" in str(exc):
                            # TODO: A race condition occurs when a subscriber
                            #  deletes itself while we're iterating over the
                            #  subscription list. For now, we just ignore it
                            #  because that occurrence will just resolve itself
                            #  and the subscriber's unsubscribe call will come
                            #  through eventually
                            pass

                            # TODO: If the above race condition is fixed, this
                            #  should be used instead of `pass`
                            # func_name = subscriber.callback.__qualname__
                            # msg = f"Pubsub callback {func_name} was called "\
                            #       f"but attempted to access a deleted " \
                            #       f"QObject:\n\t{exc}"
                            # logging.error(msg)

    def subscribe(self, topic, callback: Callable, filters=None) \
            -> Subscription:

        subscription = Subscription(topic, callback, filters)
        with self.subscriptions_lock:
            self.subscriptions[topic].add(subscription)
        return subscription

    def subscribe_streams(self, callback: Callable, stream_id=any) \
            -> Subscription:

        filters = {"stream_id": stream_id}

        return self.subscribe(ZSSTopic.STREAMS, callback, filters=filters)

    def subscribe_zones(self, callback: Callable, stream_id=any, zone_id=any) \
            -> Subscription:

        filters = {"stream_id": stream_id,
                   "zone_id": zone_id}

        return self.subscribe(ZSSTopic.ZONES, callback, filters=filters)

    def subscribe_alarms(self, callback: Callable,
                         stream_id=any, zone_id=any, alarm_id=any) \
            -> Subscription:

        filters = {"stream_id": stream_id,
                   "zone_id": zone_id,
                   "alarm_id": alarm_id}

        return self.subscribe(ZSSTopic.ALARMS, callback, filters=filters)

    def subscribe_alerts(self, callback: Callable,
                         stream_id=any, zone_id=any, alarm_id=any,
                         alert_id=any) \
            -> Subscription:

        filters = {"stream_id": stream_id,
                   "zone_id": zone_id,
                   "alarm_id": alarm_id,
                   "alert_id": alert_id}

        return self.subscribe(ZSSTopic.ALERTS, callback, filters=filters)

    def unsubscribe(self, subscription: Subscription) -> None:
        with self.subscriptions_lock:
            self.subscriptions[subscription.topic].remove(subscription)


# noinspection SpellCheckingInspection
zss_publisher = _ZSSPubSub()
