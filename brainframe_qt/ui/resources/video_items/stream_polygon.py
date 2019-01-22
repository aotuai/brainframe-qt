from typing import Union, Iterable, List

from PyQt5.QtCore import Qt, QLineF, QPointF
from PyQt5.QtGui import QColor, QPainterPath, QPolygonF
from PyQt5.QtWidgets import QGraphicsPathItem


class StreamPolygon(QGraphicsPathItem):

    def __init__(self, points: List[QPointF] = (), *,
                 border_color=None,
                 border_thickness=1,
                 border_linetype=None,
                 fill_color=None,
                 opacity=1.0,
                 close_polygon=True,
                 parent=None):

        super().__init__(parent=parent)

        self.close_polygon = close_polygon

        self.polygon = QPolygonF()
        self.path: QPainterPath = None

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

        self.draw_points(points)

    def insert_point(self, point: Union[List, QPointF]):
        if isinstance(point, list) or isinstance(point, tuple):
            point = QPointF(point[0], point[1])
        self.polygon.append(point)

    def move_point(self, old_point: QPointF, new_point: QPointF):
        """Find point of polygon nearest to old_point and move it to
        new_point
        """
        points = list(self.polygon)
        nearest_point = sorted(
            points,
            key=lambda pt: QLineF(pt, old_point).length()
        )[0]

        nearest_point.setX(new_point.x())
        nearest_point.setY(new_point.y())

        self.draw_points(points)

    def draw_points(self, points: Iterable):
        """Create polygon using points and add it to the Item, replacing
        the existing one
        """
        self.polygon = QPolygonF()
        for point in points:
            self.insert_point(point)

        self.redraw_polygon()

    def redraw_polygon(self):

        self.path = QPainterPath()
        self.path.addPolygon(self.polygon)

        if len(self.polygon) > 2 and self.close_polygon:
            self.path.closeSubpath()

        self.setPath(self.path)

    @property
    def points_list(self):
        """Returns a list in a non-QT type"""
        return [(point.x(), point.y()) for point in self.polygon]
