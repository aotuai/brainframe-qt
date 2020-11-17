import math
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QTransform

from brainframe.client.ui.resources.ui_elements.constants import \
    QColorConstants
from .line_item import LineItem
from .video_item import VideoItem


class ArrowItem(VideoItem):
    CHEVRON_LENGTH = 20
    CHEVRON_ANGLE = 45

    def __init__(self, base_point: VideoItem.PointType,
                 tip_point: VideoItem.PointType, *,
                 color: QColor = QColorConstants.Black, thickness: int = 1,
                 line_style: Qt.PenStyle = Qt.SolidLine,
                 parent: VideoItem):
        super().__init__(parent=parent)

        self.base_point = base_point
        self.tip_point = tip_point

        self._base_line = LineItem(
            (self.base_point, self.tip_point),
            color=color,
            thickness=thickness,
            line_style=line_style,
            parent=self
        )
        self._chevron_left = LineItem(
            (self.tip_point, self._chevron_left_endpoint),
            color=color,
            thickness=thickness,
            line_style=line_style,
            parent=self
        )
        self._chevron_right = LineItem(
            (self.tip_point, self._chevron_right_endpoint),
            color=color,
            thickness=thickness,
            line_style=line_style,
            parent=self
        )

    @property
    def _chevron_left_endpoint(self) -> VideoItem.PointType:
        return self._rotate_offset(self.CHEVRON_ANGLE, self.CHEVRON_LENGTH)

    @property
    def _chevron_right_endpoint(self) -> VideoItem.PointType:
        return self._rotate_offset(-self.CHEVRON_ANGLE, self.CHEVRON_LENGTH)

    def _rotate_offset(self, angle, offset: int) -> VideoItem.PointType:
        # noinspection PyTupleAssignmentBalance

        base_angle_rad = math.atan2(self.tip_point[1] - self.base_point[1],
                                    self.tip_point[0] - self.base_point[0])
        base_angle_deg = math.degrees(base_angle_rad)

        transform = QTransform() \
            .translate(*self.tip_point) \
            .rotate(base_angle_deg + 180 - angle) \
            .translate(offset, 0)

        return transform.map(0, 0)
