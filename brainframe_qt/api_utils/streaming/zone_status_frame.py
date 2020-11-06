from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
from brainframe.api.bf_codecs import ZoneStatus
from cached_property import cached_property

from brainframe.client.api_utils.detection_tracks import DetectionTrack


@dataclass
class ZoneStatusFrame:
    """A frame that may or may not have undergone processing on the server."""

    # compare=False to prevent numpy complaining about truthiness of arrays
    frame: np.ndarray = field(compare=False)
    """BGR data on the frame"""

    tstamp: float
    """The timestamp of the frame"""

    zone_statuses: Optional[Dict[str, ZoneStatus]]
    """ZoneStatuses for the frame"""

    has_new_statuses: bool
    """True if this processed frame contains new zone statuses that have not
    appeared in previous processed frames"""

    tracks: Optional[List[DetectionTrack]]
    """DetectionTrack history for the frame"""

    @cached_property
    def frame_rgb(self):
        """Flip the BGR channels to RGB"""
        return self.frame[..., ::-1].copy()
