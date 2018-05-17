from typing import Union, List

from PyQt5.QtCore import QLineF, QPointF, QPoint, Qt
from PyQt5.QtGui import QColor, QPolygonF
from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsTextItem


class StreamPolygon(QGraphicsPolygonItem):
    def __init__(self, points: List[QPointF] = (), *,
                 border_color=None,
                 border_thickness=1,
                 border_linetype=None,
                 fill_color=None,
                 opacity=1.0,
                 parent=None):
        self.polygon = QPolygonF()
        super().__init__(self.polygon, parent=parent)

        # Initialize each point, in case the input is a list
        for point in points:
            self.insert_point(point)

        # Use border color unless manually set
        # if fill_color is None:
        #     fill_color = border_color

        # Set the opacity of the polygon
        self.setOpacity(opacity)

        pen = self.pen()
        brush = self.brush()

        # Apply the border color
        if border_color:
            pen.setColor(border_color)

        # If there's a fill, apply the fill color
        if fill_color:
            self.fill_color = QColor(fill_color)
            brush.setColor(fill_color)
            brush.setStyle(Qt.SolidPattern)

        if border_linetype:
            pen.setStyle(border_linetype)

        # Apply thickness
        pen.setWidth(border_thickness)
        pen.setJoinStyle(Qt.RoundJoin)

        # Apply the styles
        self.setPen(pen)
        self.setBrush(brush)

    def insert_point(self, point: Union[List, QPointF]):
        if isinstance(point, list) or isinstance(point, tuple):
            point = QPointF(point[0], point[1])
        self.polygon.append(point)
        self.setPolygon(self.polygon)

    def move_point(self, old_point: QPointF, new_point: QPointF):
        """Find point of polygon nearest to old_point and move it to
        new_point
        """
        points = list(self.polygon)
        nearest_point = sorted(points,
                               key=lambda pt: QLineF(pt, old_point).length())[0]

        nearest_point.setX(new_point.x())
        nearest_point.setY(new_point.y())

        self.polygon = QPolygonF(points)
        self.setPolygon(self.polygon)

    @property
    def points_list(self):
        """Returns a list in a non-QT type"""
        return [(point.x(), point.y())
                for point in self.polygon]


class StreamLabelBox(StreamPolygon):
    """This is a textbox that is intended to look pretty and go on top of
    detection or zone objects"""

    def __init__(self, title_text, top_left, parent=None):
        # Create the text item
        self.label_text = QGraphicsTextItem(title_text, parent=parent)
        self.label_text.setPos(QPoint(int(top_left[0]), int(top_left[1])))
        self.label_text.setDefaultTextColor(QColor(255, 255, 255))

        rect = self.label_text.sceneBoundingRect().getCoords()
        coords = [QPointF(rect[0], rect[1]),
                  QPointF(rect[2], rect[1]),
                  QPointF(rect[2], rect[3]),
                  QPointF(rect[0], rect[3])]

        super().__init__(points=coords,
                         border_color=parent.pen().color(),
                         fill_color=parent.pen().color(),
                         border_thickness=1,
                         opacity=0.35,
                         parent=parent)
        self.label_text.setZValue(self.zValue() + 1)
