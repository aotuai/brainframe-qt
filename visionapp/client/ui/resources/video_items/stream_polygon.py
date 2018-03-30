from typing import Union, List
from enum import Enum

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QPolygonF
from PyQt5.QtWidgets import QGraphicsPolygonItem


class StreamPolygon(QGraphicsPolygonItem):
    # noinspection PyArgumentList
    # PyCharm incorrectly complains
    # TODO: Alex: Are there more types of polygons?

    def __init__(self, points=(), *,
                 border_color=Qt.red, border_thickness=5,
                 fill_color=Qt.red, fill_alpha=128, parent=None):
        self.polygon = QPolygonF()
        super().__init__(self.polygon, parent=parent)

        # Initialize each point, in case the input is a list
        for point in points:
            self.insert_point(point)



        # Use border color unless manually set
        if fill_color is None:
            fill_color = border_color

        self.border_color = None
        self.fill_color = None
        self.fill_alpha = fill_alpha
        self.border_thickness = None

        # Apply the colors
        self.set_color(border_color, fill_color)

        # Apply thickness
        self._apply_border_thickness(border_thickness)

    def insert_point(self, point: Union[List, QPointF]):
        if isinstance(point, list) or isinstance(point, tuple):
            point = QPointF(point[0], point[1])
        self.polygon.append(point)
        self.setPolygon(self.polygon)

    def set_color(self, border_color=None, fill_color=None):
        """Set border color and fill_color of Polygon

        If fill_color is None, it is set to border_color
        """
        if border_color:
            self.border_color = border_color
            self._apply_border_color(border_color)
        if not fill_color:
            fill_color = border_color
        self.fill_color = QColor(fill_color)
        self.fill_color.setAlpha(self.fill_alpha)

        self._apply_fill_color(fill_color)

    def _apply_border_color(self, border_color):

        pen = self.pen()
        pen.setColor(border_color)
        self.setPen(pen)

    def _apply_fill_color(self, fill_color):

        brush = self.brush()
        brush.setColor(fill_color)
        self.setBrush(brush)

    def _apply_border_thickness(self, border_thickness):

        self.border_thickness = border_thickness

        pen = self.pen()
        pen.setWidth(border_thickness)
        self.setPen(pen)


class DetectionPolygon(StreamPolygon):
    """Render a Detection polygon with a title and behaviour information"""


class ZonePolygon(StreamPolygon):
    """No changes yet"""