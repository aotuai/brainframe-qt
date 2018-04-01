from typing import Union, List

from PyQt5.QtCore import QPointF, QPoint, Qt
from PyQt5.QtGui import QColor, QPolygonF
from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsTextItem


class StreamPolygon(QGraphicsPolygonItem):
    def __init__(self, points=(), *,
                 border_color=Qt.red, border_thickness=5,
                 fill_color=None, opacity=1.0, parent=None):
        self.polygon = QPolygonF()
        super().__init__(self.polygon, parent=parent)

        # Initialize each point, in case the input is a list
        for point in points:
            self.insert_point(point)

        # Use border color unless manually set
        # if fill_color is None:
        #     fill_color = border_color

        self.setOpacity(opacity)
        self.border_color = None
        self.fill_color = None
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
        if fill_color:
            self.fill_color = QColor(fill_color)
            self._apply_fill_color(fill_color)

    @property
    def points_list(self):
        """Returns a list in a non-QT type"""
        return [(point.x(), point.y())
                for point in self.polygon]

    def _apply_border_color(self, border_color):
        pen = self.pen()
        pen.setColor(border_color)
        self.setPen(pen)

    def _apply_fill_color(self, fill_color):
        brush = self.brush()
        brush.setColor(fill_color)
        brush.setStyle(Qt.SolidPattern)
        self.setBrush(brush)

    def _apply_border_thickness(self, border_thickness):

        self.border_thickness = border_thickness

        pen = self.pen()
        pen.setWidth(border_thickness)
        self.setPen(pen)


class StreamLabelBox(StreamPolygon):
    """This is a textbox that is intended to look pretty and go on top of
    detection or zone objects"""

    def __init__(self, title_text, top_left, parent=None):
        # Create the text item
        self.label_text = QGraphicsTextItem(title_text, parent=parent)
        self.label_text.setPos(QPoint(int(top_left[0]), int(top_left[1])))
        self.label_text.setDefaultTextColor(QColor(255, 255, 255))

        rect = self.label_text.sceneBoundingRect().getCoords()
        coords = [[rect[0], rect[1]],
                  [rect[2], rect[1]],
                  [rect[2], rect[3]],
                  [rect[0], rect[3]]]

        super().__init__(points=coords,
                         border_color=parent.border_color,
                         fill_color=parent.border_color,
                         border_thickness=parent.border_thickness,
                         opacity=0.35,
                         parent=parent)
        self.label_text.setZValue(self.zValue() + 1)
