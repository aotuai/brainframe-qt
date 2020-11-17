import typing
from typing import Iterable, List, Optional

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QPainterPath, QPolygonF
from PyQt5.QtWidgets import QGraphicsPathItem

from brainframe.client.ui.resources.ui_elements.constants import \
    QColorConstants
from .video_item import VideoItem


class PolygonItem(QGraphicsPathItem):

    def __init__(self, points: List[VideoItem.PointType],
                 *, parent: VideoItem,
                 border_color: QColor = QColorConstants.Black,
                 fill_color: QColor = QColorConstants.Transparent):
        super().__init__(parent)

        self._border_color = typing.cast(QColor, None)
        self.border_color = border_color

        self._border_thickness: int = 1
        self._border_linetype: Optional[Qt.PenStyle] = None

        self._fill_color = typing.cast(QColor, None)
        self.fill_color = fill_color

        self.close_polygon: bool = True

        self.polygon = typing.cast(QPolygonF, None)
        self.points = points

        self._init_style()

    def _init_style(self):
        pen = self.pen()

        pen.setJoinStyle(Qt.RoundJoin)
        pen.setCapStyle(Qt.RoundCap)

        self.setPen(pen)

    @property
    def points(self) -> List[QPointF]:
        return list(self.polygon)

    @points.setter
    def points(self, points: Iterable[VideoItem.PointType]):
        points = [QPointF(*point) for point in points]
        self.polygon = QPolygonF(points)

        path = QPainterPath()
        path.addPolygon(self.polygon)

        if len(self.polygon) > 2 and self.close_polygon:
            path.closeSubpath()

        self.setPath(path)

    def add_point(self, point: VideoItem.PointType) -> None:
        point = QPointF(*point)
        # TODO: Does not modify PainterPath
        self.polygon.append(point)

    @property
    def border_color(self) -> QColor:
        return self._border_color

    @border_color.setter
    def border_color(self, border_color: QColor):
        self._border_color = border_color

        pen = self.pen()
        pen.setColor(border_color)

        self.setPen(pen)

    @property
    def border_linetype(self) -> Optional[Qt.PenStyle]:
        return self._border_linetype

    @border_linetype.setter
    def border_linetype(self, border_linetype: Optional[Qt.PenStyle]):
        self._border_linetype = border_linetype

        pen = self.pen()
        pen.setStyle(border_linetype)

        self.setPen(pen)

    @property
    def border_thickness(self) -> int:
        return self._border_thickness

    @border_thickness.setter
    def border_thickness(self, border_thickness: int):
        self._border_thickness = border_thickness

        pen = self.pen()
        pen.setWidth(border_thickness)

        self.setPen(pen)

    @property
    def fill_color(self) -> Optional[QColor]:
        return self._fill_color

    @fill_color.setter
    def fill_color(self, fill_color: QColor):
        self._fill_color = fill_color

        brush = self.brush()
        brush.setColor(fill_color)
        brush.setStyle(Qt.SolidPattern)

        self.setBrush(brush)
