from typing import List

from brainframe.client.api.stubs.base_stub import BaseStub, DEFAULT_TIMEOUT
from brainframe.client.api.codecs import Zone


class ZoneStubMixin(BaseStub):
    """Provides stubs for calling APIs to get, set, and delete zones."""

    def get_zones(self, stream_id=None,
                  timeout=DEFAULT_TIMEOUT) -> List[Zone]:
        """Gets all zones.
        :param stream_id: If set, only zones in the stream with this ID are
            returned
        :param timeout: The timeout to use for this request
        :return: Zones
        """
        req = "/api/zones"
        params = {"stream_id": stream_id} if stream_id else None
        data, _ = self._get_json(req, timeout, params=params)
        zones = [Zone.from_dict(j) for j in data]
        return zones

    def get_zone(self, zone_id,
                 timeout=DEFAULT_TIMEOUT) -> Zone:
        """Get a specific zone.
        :param zone_id: The ID of the zone to get
        :param timeout: The timeout to use for this request
        """
        req = f"/api/zones/{zone_id}"
        data, _ = self._get_json(req, timeout)
        return Zone.from_dict(data)

    def set_zone(self, zone: Zone,
                 timeout=DEFAULT_TIMEOUT):
        """Update or create a zone. If the Zone doesn't exist, the zone.id
        must be None. An initialized Zone with an ID will be returned.
        :param zone: A Zone object
        :param timeout: The timeout to use for this request
        :return: Zone, initialized with an ID
        """
        req = "/api/zones"
        data = self._post_codec(req, timeout, zone)
        new_zone = Zone.from_dict(data)
        return new_zone

    def delete_zone(self, zone_id: int,
                    timeout=DEFAULT_TIMEOUT):
        """Deletes a zone with the given ID.
        :param zone_id: The ID of the zone to delete
        :param timeout: The timeout to use for this request
        """
        req = f"/api/zones/{zone_id}"
        self._delete(req, timeout)
