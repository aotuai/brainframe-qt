from typing import Dict, List, Generator

import ujson

from brainframe.client.api.stubs.stub import Stub
from brainframe.client.api.codecs import ZoneStatus

ZONE_STATUS_TYPE = Dict[int, Dict[str, ZoneStatus]]


class ZoneStatusStubMixin(Stub):
    """Provides stubs for calling APIs to get zone statuses."""

    def get_latest_zone_statuses(self) -> ZONE_STATUS_TYPE:
        """Get all ZoneStatuses
        This method gets ALL of the latest processed zone statuses for every
        zone for every stream. The call is intentionally broad and large so as
        to lower the overhead of pinging the server and waiting for a return.

        All active streams will have a key in the output dict.
        :return:
        {
            stream_id1: {"Front Porch": ZoneStatus, "Some Place": ZoneStatus},
            stream_id2: {"Entrance": ZoneStatus}
        }
        """
        req = "/api/streams/status"
        data, _ = self._get_json(req)

        # Convert ZoneStatuses to Codecs
        out = {int(s_id): {key: ZoneStatus.from_dict(val)
                           for key, val in statuses.items()}
               for s_id, statuses in data.items()}
        return out

    def get_zone_status_stream(self) -> Generator[ZONE_STATUS_TYPE, None, None]:
        req = "/api/streams/statuses"

        def zone_status_iterator():
            resp = self._get(req)
            for packet in resp.iter_lines(delimiter=b"\r\n"):
                if packet == b'':
                    continue

                # Parse the line
                zone_statuses_dict = ujson.loads(packet)

                processed = {int(s_id): {key: ZoneStatus.from_dict(val)
                                         for key, val in statuses.items()}
                             for s_id, statuses in zone_statuses_dict.items()}
                yield processed

        return zone_status_iterator()
