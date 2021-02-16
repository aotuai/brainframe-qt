import random
from typing import Dict, Optional

from PyQt5.QtGui import QColor
from brainframe.api.bf_codecs import Detection

from brainframe_qt.api_utils.detection_tracks import DetectionTrack
from brainframe_qt.ui.resources.config import QSettingsRenderConfig
from brainframe_qt.ui.resources.video_items.base import VideoItem
from .detection_label_item import DetectionLabelItem
from .detection_polygon_item import DetectionPolygonItem
from .detection_track_item import DetectionTrackItem


class DetectionItem(VideoItem):
    _qcolor_cache: Dict[str, QColor] = {}

    def __init__(self, detection: Detection, *,
                 track: Optional[DetectionTrack],
                 render_config: QSettingsRenderConfig,
                 parent: Optional[VideoItem] = None):
        super().__init__(parent=parent)

        self.detection = detection
        self.track = track

        self.detection_polygon = DetectionPolygonItem(
            detection, self.draw_color,
            render_config=render_config, parent=self)
        self.detection_label = DetectionLabelItem(
            detection, self.draw_color,
            render_config=render_config, parent=self)

        self.detection_track: Optional[DetectionTrackItem] = None
        if render_config.show_detection_tracks:
            self.detection_track = DetectionTrackItem(track, parent=self)

    @property
    def draw_color(self) -> QColor:
        seed = self.detection.class_name
        if seed not in self._qcolor_cache:
            rand_seed = random.Random(seed)
            hue = rand_seed.random()
            self._qcolor_cache[seed] = QColor.fromHsvF(hue, 1.0, 1.0)

        return self._qcolor_cache[seed]
