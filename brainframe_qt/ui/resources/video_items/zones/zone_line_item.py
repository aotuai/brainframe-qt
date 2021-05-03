import math
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QTransform
from brainframe.api.bf_codecs import Zone

from brainframe_qt.ui.resources.config import RenderSettings
from brainframe_qt.ui.resources.video_items.base import ArrowItem, \
    LineItem, VideoItem
from .abstract_zone_item import AbstractZoneItem


class ZoneLineItem(AbstractZoneItem, VideoItem):
    ARROW_LENGTH = 40

    def __init__(self, zone: Zone, *,
                 render_config: RenderSettings,
                 parent: VideoItem,
                 color: QColor = AbstractZoneItem.BORDER_COLOR,
                 thickness: int = AbstractZoneItem.BORDER_THICKNESS,
                 line_style: Qt.PenStyle = Qt.SolidLine):
        AbstractZoneItem.__init__(self, zone)
        VideoItem.__init__(self, parent=parent)

        self.color = color
        self.thickness = thickness
        self.line_style = line_style

        self.line_item = LineItem(self.zone_coords, color=color,
                                  thickness=thickness, line_style=line_style,
                                  parent=self)
        self.line_direction_item = self._init_line_direction_item()

    def _init_line_direction_item(self) -> ArrowItem:
        base_point = self.line_centerpoint
        tip_point = self._rotate_offset(90, self.ARROW_LENGTH)

        line_direction_item = ArrowItem(
            base_point, tip_point,
            color=self.color,
            thickness=self.thickness // 2,
            parent=self
        )

        return line_direction_item

    @property
    def line_centerpoint(self) -> VideoItem.PointType:
        # noinspection PyTupleAssignmentBalance
        left_point, right_point = self.zone_coords
        x = (left_point[0] + right_point[0]) / 2
        y = (left_point[1] + right_point[1]) / 2

        return x, y

    # TODO: Duplicates function in ArrowItem
    def _rotate_offset(self, angle, offset: int) -> VideoItem.PointType:
        # noinspection PyTupleAssignmentBalance
        left_point, right_point = self.zone_coords

        base_angle_rad = math.atan2(right_point[1] - left_point[1],
                                    right_point[0] - left_point[0])
        base_angle_deg = math.degrees(base_angle_rad)

        transform = QTransform() \
            .translate(*self.line_centerpoint) \
            .rotate(base_angle_deg + 180 - angle) \
            .translate(offset, 0)

        return transform.map(0, 0)
