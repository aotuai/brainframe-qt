from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
from brainframe.api.bf_codecs import ZoneStatus

from brainframe.client.api_utils.detection_tracks import DetectionTrack


@dataclass(eq=False)  # eq=False as np frames can't be compared using __eq__
class ZoneStatusFrame:
    """A frame that may or may not have undergone processing on the server."""

    frame: np.ndarray
    """RGB data on the frame"""

    tstamp: float
    """The timestamp of the frame"""

    zone_statuses: Optional[Dict[str, ZoneStatus]]
    """ZoneStatuses for the frame"""

    tracks: Optional[List[DetectionTrack]]
    """DetectionTrack history for the frame"""

    frame_metadata: 'ZoneStatusFrameMeta' \
        = field(default_factory=lambda: ZoneStatusFrameMeta())


@dataclass
class ZoneStatusFrameMeta:
    client_buffer_full: bool = False
