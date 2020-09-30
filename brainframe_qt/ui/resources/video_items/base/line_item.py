import typing
from typing import Tuple

from PyQt5.QtCore import QLineF, QPointF, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsLineItem

from brainframe.client.ui.resources.ui_elements.constants import \
    QColorConstants
from .video_item import VideoItem


class LineItem(QGraphicsLineItem):

    def __init__(self, end_points: Tuple[VideoItem.PointType], *,
                 color: QColor = QColorConstants.Black,
                 thickness: int = 1, line_style: Qt.PenStyle = Qt.SolidLine,
                 parent: VideoItem):
        self.end_points = end_points

        super().__init__(self._line, parent=parent)

        self._color = typing.cast(QColor, None)
        self.color = color

        self._thickness = typing.cast(int, None)
        self.thickness = thickness

        self._line_style = typing.cast(Qt.PenStyle, None)
        self.line_style = line_style

    @property
    def _line(self) -> QLineF:
        points = [QPointF(*point) for point in self.end_points]
        return QLineF(*points)

    @property
    def color(self) -> QColor:
        return self._color

    @color.setter
    def color(self, color: QColor):
        self._color = color

        pen = self.pen()
        pen.setColor(color)

        self.setPen(pen)

    @property
    def line_style(self) -> Qt.PenStyle:
        return self._line_style

    @line_style.setter
    def line_style(self, line_style: Qt.PenStyle):
        self._line_style = line_style

        pen = self.pen()
        pen.setStyle(line_style)

        self.setPen(pen)

    @property
    def thickness(self) -> int:
        return self._thickness

    @thickness.setter
    def thickness(self, thickness: int):
        self._thickness = thickness

        pen = self.pen()
        pen.setWidth(thickness)

        self.setPen(pen)
