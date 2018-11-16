from brainframe.client.api.stubs.stub import Stub
from brainframe.client.api.codecs import ZoneAlarm


class ZoneAlarmStubMixin(Stub):
    """Provides stubs for calling APIs related to getting zone alarms."""

    def get_zone_alarm(self, alarm_id) -> ZoneAlarm:
        """Gets the zone alarm with the given ID.

        :param alarm_id: The ID of the alarm to get
        :return: The alarm
        """
        req = f"/api/zone_alarms/{alarm_id}"
        data = self._get(req)

        return ZoneAlarm.from_dict(data)

    def set_zone_alarm(self, alarm: ZoneAlarm) -> ZoneAlarm:
        """Creates or updates a zone alarm.

        A new zone alarm is created if the given zone alarm's ID is None.

        :param alarm: The zone alarm to create or update
        :return: Created or updated zone alarm
        """
        req = f"/api/zone_alarms"
        data = self._post_codec(req, alarm)

        return ZoneAlarm.from_dict(data)
