from typing import List

from brainframe.client.api.stubs.stub import Stub
from brainframe.client.api.codecs import Zone


class ZoneStubMixin(Stub):
    """Provides stubs for calling APIs to get, set, and delete zones."""

    def get_zones(self, stream_id=None) -> List[Zone]:
        """Gets all zones.
        :param stream_id: If set, only zones in the stream with this ID are
            returned
        :return: Zones
        """
        req = "/api/zones"
        params = {"stream_id": stream_id} if stream_id else None
        data, _ = self._get_json(req, params=params)
        zones = [Zone.from_dict(j) for j in data]
        return zones

    def get_zone(self, zone_id) -> Zone:
        """Get a specific zone.
        :param zone_id: The ID of the zone to get
        """
        req = f"/api/zones/{zone_id}"
        data, _ = self._get_json(req)
        return Zone.from_dict(data)

    def set_zone(self, zone: Zone):
        """Update or create a zone. If the Zone doesn't exist, the zone.id
        must be None. An initialized Zone with an ID will be returned.
        :param zone: A Zone object
        :return: Zone, initialized with an ID
        """
        req = "/api/zones"
        data = self._post_codec(req, zone)
        new_zone = Zone.from_dict(data)
        return new_zone

    def delete_zone(self, zone_id: int):
        """Deletes a zone with the given ID.
        :param zone_id: The ID of the zone to delete
        """
        req = f"/api/zones/{zone_id}"
        self._delete(req)
