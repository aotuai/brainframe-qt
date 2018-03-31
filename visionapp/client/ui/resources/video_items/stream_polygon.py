import random
from typing import Union, List
from enum import Enum

from PyQt5.QtCore import QPointF, QPoint, Qt
from PyQt5.QtGui import QColor, QPolygonF
from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsTextItem

from visionapp.client.api import codecs


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


class DetectionPolygon(StreamPolygon):
    """Render a Detection polygon with a title and behaviour information"""
    MAX_SECONDS_OLD = 3
    """After a certain amount of time, the detection will be transparent"""

    def __init__(self, det: codecs.Detection, seconds_old=0, parent=None):
        """
        :param detection: The Detection object to render
        :param seconds_old: Fades the detection by a standard amount based on
        it's age.
        :param parent:
        """
        # Choose a color for this class name
        rand_seed = random.Random(det.class_name)
        hue = rand_seed.random()

        class_color = QColor.fromHsvF(hue, 1.0, 1.0)

        # Choose the opacity based on the age of the detection
        clamped_age = sorted([0, seconds_old, self.MAX_SECONDS_OLD])[1]
        opacity = 1 - clamped_age / self.MAX_SECONDS_OLD
        opacity += 0.05  # Minimum opacity for a detection

        super().__init__(det.coords,
                         border_color=class_color,
                         border_thickness=3,
                         opacity=opacity, parent=parent)

        # Create the description box
        top_left = det.coords[0]
        text = det.class_name + "\n" + "".join([a.category + ": " + a.value
                                           for a in det.attributes])
        self.label_box = StreamLabelBox(text,
                                        top_left=top_left,
                                        parent=self)


class ZonePolygon(StreamPolygon):
    """No changes yet"""


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
                         parent=parent)
        self.label_text.setZValue(self.zValue() + 1)
