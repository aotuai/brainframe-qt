from dataclasses import dataclass, field
from datetime import timedelta
from typing import Dict, List, Optional

import numpy as np
from PyQt5.QtGui import QImage, QPixmap

from brainframe.api.bf_codecs import ZoneStatus

from brainframe_qt.api_utils.detection_tracks import DetectionTrack


@dataclass(eq=False)  # eq=False as np frames can't be compared using __eq__
class ZoneStatusFrame:
    """A frame that may or may not have undergone processing on the server."""

    frame: QPixmap
    """Frame as a QPixmap"""

    tstamp: float
    """The timestamp of the frame"""

    zone_statuses: Optional[Dict[str, ZoneStatus]] = None
    """ZoneStatuses for the frame"""

    tracks: Optional[List[DetectionTrack]] = None
    """DetectionTrack history for the frame"""

    frame_metadata: 'ZoneStatusFrameMeta' \
        = field(default_factory=lambda: ZoneStatusFrameMeta())

    # Cython currently isn't working with @dataclass or NamedTuple, but this
    # fixes it. There's a PR to fix this, and here's the relevant issue:
    # https://github.com/cython/cython/issues/2552
    __annotations__ = {
        'frame': np.ndarray,
        'tstamp': float,
        'zone_statuses': Optional[Dict[str, ZoneStatus]],
        'tracks': Optional[List[DetectionTrack]],
        'frame_metadata': 'ZoneStatusFrameMeta',
    }

    @staticmethod
    def pixmap_from_numpy_frame(frame: np.ndarray) -> QPixmap:
        height, width, channel = frame.shape
        bytes_per_line = width * 3
        image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(image)


@dataclass
class ZoneStatusFrameMeta:
    no_analysis: bool = False
    analysis_latency: timedelta = timedelta(seconds=0)
    client_buffer_full: bool = False

    # Cython currently isn't working with @dataclass or NamedTuple, but this
    # fixes it. There's a PR to fix this, and here's the relevant issue:
    # https://github.com/cython/cython/issues/2552
    __annotations__ = {
        'no_analysis': bool,
        'analysis_latency': timedelta,
        'client_buffer_full': bool
    }
