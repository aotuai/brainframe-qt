from typing import List

from PyQt5.QtGui import QColor
from brainframe.api.bf_codecs import Detection

from brainframe.client.ui.resources.config import QSettingsRenderConfig
from brainframe.client.ui.resources.video_items.base import PolygonItem, \
    VideoItem


class DetectionPolygonItem(PolygonItem):

    def __init__(self, detection: Detection, color: QColor, *,
                 render_config: QSettingsRenderConfig,
                 parent: VideoItem):
        self.detection = detection
        self.render_config = render_config

        super().__init__(self.polygon_points,
                         border_color=color, parent=parent)

    @property
    def polygon_points(self) -> List[VideoItem.PointType]:
        if self.render_config.use_polygons:
            return self.detection.coords
        else:
            return self.detection.bbox
