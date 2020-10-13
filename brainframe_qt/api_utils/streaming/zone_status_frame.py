from typing import List

import numpy as np
from brainframe.api.bf_codecs import ZoneStatus

from brainframe.client.api_utils.detection_tracks import DetectionTrack


class ZoneStatusFrame:
    """A frame that may or may not have undergone processing on the server."""

    def __init__(self, frame, tstamp, zone_statuses, has_new_statuses, tracks):
        """
        :param frame: RGB data on the frame
        :param tstamp: The timestamp of the frame
        :param zone_statuses: A zone status that is most relevant to this
            frame, though it might not be a result of this frame specifically
        :param has_new_statuses: True if this processed frame contains new
            zone statuses that have not appeared in previous processed frames
        """
        self.frame: np.ndarray = frame
        self.tstamp: float = tstamp
        self.zone_statuses: List[ZoneStatus] = zone_statuses
        self.has_new_zone_statuses = has_new_statuses
        self.tracks: List[DetectionTrack] = tracks

        # Cachable properties
        self._frame_rgb = None

    @property
    def frame_rgb(self):
        """Flip the BGR channels to RGB"""
        if not self._frame_rgb:
            self._frame_rgb = self.frame[..., ::-1].copy()
        return self._frame_rgb
