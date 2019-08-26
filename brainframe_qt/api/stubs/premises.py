from typing import List

from brainframe.client.api.stubs.stub import Stub
from brainframe.client.api.codecs import Premises


class PremisesStubMixin(Stub):
    """Provides stubs for calling APIs to get, set, and delete zones."""

    def get_premises(self) -> List[Premises]:
        """Gets all zones.
        :param stream_id: If set, only zones in the stream with this ID are
            returned
        :return: Zones
        """
        req = "/api/premises"
        data, _ = self._get_json(req)
        zones = [Premises.from_dict(j) for j in data]
        return zones

    def set_zone(self, premises: Premises):
        """Update or create a premises. If the Premises doesn't exist, the
        premises.id must be None. An initialized Premises with an ID will be
        returned.
        :param premises: A Premises object
        :return: Premises, initialized with an ID
        """

        req = "/api/premises"
        data = self._post_codec(req, premises)
        new_premises = Premises.from_dict(data)
        return new_premises
