from typing import List

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QMouseEvent, QPolygonF
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsPolygonItem

from visionapp.client.ui.resources.stream_widget import StreamWidget


class VideoTaskConfig(StreamWidget):

    def __init__(self, parent=None, stream_conf=None, frame_rate=30):
        super().__init__(stream_conf, frame_rate, parent)

        self.points: List[QPointF] = []
        """List of click points. Used to draw Polygon"""

        self.zones: List[ClickPolygon] = []
        """List of zones"""

        self.unconfirmed_polygon: ClickPolygon = None

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Called when mouse click is _released_ on Widget"""

        # Ignore mouseEvents (until new region is begun)
        if self.unconfirmed_polygon is not None:

            # Get the coordinates of the mouse press in the scene's coordinates
            click = self.mapToScene(event.pos())

            # Create new circle
            circle = ClickCircle(click.x(), click.y(),
                                 diameter=10,
                                 color=Qt.red)
            self.scene_.addItem(circle)

            # Create new point
            self.points.append(click)
            self.unconfirmed_polygon.insert_point(click)

            # Draw item if not already drawn
            if self.unconfirmed_polygon not in self.scene_.items():
                self.scene_.addItem(self.unconfirmed_polygon)

        super().mouseReleaseEvent(event)

    def start_new_polygon(self):
        self.unconfirmed_polygon = ClickPolygon()

    def confirm_unconfirmed_polygon(self):
        self.zones.append(self.unconfirmed_polygon)
        self.unconfirmed_polygon.set_color(Qt.green)

        ret = self.unconfirmed_polygon.polygon

        # Polygon is no longer "unconfirmed" so delete that reference
        self.unconfirmed_polygon = None

        return ret

    def clear_unconfirmed_polygon(self):
        self.scene_.removeItem(self.unconfirmed_polygon)
        self.unconfirmed_polygon = None


class ClickCircle(QGraphicsEllipseItem):
    """Debug class used for showing mouse clicks on video"""

    def __init__(self, x, y, *,
                 diameter=None, radius=None, color=Qt.black, parent=None):
        if radius is not None:
            diameter = radius * 2
        self.diameter = diameter

        self.x = x - (diameter // 2)
        self.y = y - (diameter // 2)

        self.color = color

        super().__init__(self.x, self.y, diameter, diameter, parent=parent)

        pen = self.pen()
        pen.setColor(color)
        self.setPen(pen)


class ClickPolygon(QGraphicsPolygonItem):

    def __init__(self, points=(), *,
                 border_color=Qt.red, border_thickness=5,
                 fill_color=Qt.red, fill_alpha=128, parent=None):

        self.polygon = QPolygonF(points)

        super().__init__(self.polygon, parent=parent)

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

    def insert_point(self, point: QPointF):
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
