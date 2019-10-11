from typing import Optional, List

from brainframe.client.api.stubs.base_stub import BaseStub, DEFAULT_TIMEOUT
from brainframe.client.api.codecs import ZoneAlarm


class ZoneAlarmStubMixin(BaseStub):
    """Provides stubs for calling APIs related to getting zone alarms."""

    def get_zone_alarm(self, alarm_id,
                       timeout=DEFAULT_TIMEOUT) -> ZoneAlarm:
        """Gets the zone alarm with the given ID.

        :param alarm_id: The ID of the alarm to get
        :param timeout: The timeout to use for this request
        :return: The alarm
        """
        req = f"/api/zone_alarms/{alarm_id}"
        data, _ = self._get_json(req, timeout)

        return ZoneAlarm.from_dict(data)

    def get_zone_alarms(self, stream_id: Optional[int] = None,
                        zone_id: Optional[int] = None,
                        timeout=DEFAULT_TIMEOUT) -> List[ZoneAlarm]:
        """Gets all zone alarms that fit the given filters.

        :param stream_id: If supplied, only zone alarms that are for a zone in
            this stream will be returned
        :param zone_id: if supplied, only zone alarms attached to this zone
            will be returned
        :param timeout: The timeout to use for this request
        :return: Zone alarms
        """
        req = f"/api/zone_alarms"

        params = {}
        if stream_id is not None:
            params["stream_id"] = stream_id
        if zone_id is not None:
            params["zone_id"] = zone_id

        data, _ = self._get_json(req, timeout, params=params)

        return [ZoneAlarm.from_dict(a) for a in data]

    def set_zone_alarm(self, alarm: ZoneAlarm,
                       timeout=DEFAULT_TIMEOUT) -> ZoneAlarm:
        """Creates or updates a zone alarm.

        A new zone alarm is created if the given zone alarm's ID is None.

        :param alarm: The zone alarm to create or update
        :param timeout: The timeout to use for this request
        :return: Created or updated zone alarm
        """
        req = f"/api/zone_alarms"
        data = self._post_codec(req, timeout, alarm)

        return ZoneAlarm.from_dict(data)

    def delete_zone_alarm(self, alarm_id,
                          timeout=DEFAULT_TIMEOUT):
        """Deletes the zone alarm with the given ID.

        :param alarm_id: The ID of the zone alarm to delete
        :param timeout: The timeout to use for this request
        """
        req = f"/api/zone_alarms/{alarm_id}"
        self._delete(req, timeout)

