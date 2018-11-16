from typing import Dict, List

from brainframe.client.api.stubs.stub import Stub
from brainframe.client.api.codecs import ZoneStatus


class ZoneStatusStubMixin(Stub):
    """Provides stubs for calling APIs to get zone statuses."""

    def get_latest_zone_statuses(self) -> Dict[int, List[ZoneStatus]]:
        """Get all ZoneStatuses
        This method gets ALL of the latest processed zone statuses for every
        zone for every stream. The call is intentionally broad and large so as
        to lower the overhead of pinging the server and waiting for a return.

        All active streams will have a key in the output dict.
        :return:
        {stream_id1: [ZoneStatus, ZoneStatus], stream_id2: [ZoneStatus]}
        """
        req = "/api/streams/status/"
        data = self._get(req)

        # Convert ZoneStatuses to Codecs
        out = {int(s_id): [ZoneStatus.from_dict(status)
                           for status in statuses]
               for s_id, statuses in data.items()}
        return out
