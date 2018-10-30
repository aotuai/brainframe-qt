from typing import List

from brainframe.client.api.stubs.stub import Stub
from brainframe.client.api.codecs import Zone


class ZoneStubMixin(Stub):
    """Provides stubs for calling APIs to get, set, and delete zones."""

    def get_zones(self, stream_id) -> List[Zone]:
        """Returns a list of Zone's associated with that stream"""
        req = f"/api/streams/{stream_id}/zones"
        data = self._get(req)
        zones = [Zone.from_dict(j) for j in data]
        return zones

    def get_zone(self, stream_id, zone_id) -> Zone:
        """Get a specific zone.
        :param stream_id: The ID of the stream that the desired zone is for
        :param zone_id: The ID of the zone to get
        """
        data = self.get_zones(stream_id)
        zones = [zone for zone in data if zone.id == zone_id]
        assert len(zones) != 0, ("A zone with that stream_id and zone_id could"
                                 " not be found!")
        return zones[0]

    def set_zone(self, stream_id: int, zone: Zone):
        """Update or create a zone. If the Zone doesn't exist, the zone.id
        must be None. An initialized Zone with an ID will be returned.
        :param stream_id: The stream_id that this zone exists in
        :param zone: A Zone object
        :return: Zone, initialized with an ID
        """
        req = f"/api/streams/{stream_id}/zones"
        data = self._post_codec(req, zone)
        new_zone = Zone.from_dict(data)
        return new_zone

    def delete_zone(self, stream_id: int, zone_id: int):
        """Deletes a zone with the given ID.
        :param stream_id: The ID of the stream the zone is a part of
        :param zone_id: The ID of the zone to delete
        """
        req = f"/api/streams/{stream_id}/zones/{zone_id}"
        self._delete(req)
