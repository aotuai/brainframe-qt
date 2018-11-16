from typing import Union, Optional

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QGraphicsEllipseItem


class ClickCircle(QGraphicsEllipseItem):
    """Debug class used for showing mouse clicks on video"""

    def __init__(self, x, y, *,
                 diameter=None, radius=None, border_thickness=1,
                 color=Qt.black, parent=None):

        if radius is not None:
            diameter = radius * 2

        self.diameter = diameter
        self.x = 0
        self.y = 0

        self.color = color

        super().__init__(0, 0, diameter, diameter, parent=parent)

        pen = self.pen()
        pen.setColor(color)
        pen.setWidth(border_thickness)
        self.setPen(pen)

        self.setPos(x, y)

    def setPos(self, x: Union[float, QPointF], y: Optional[float] = None):
        """Set position relative to center of circle instead of top left"""

        if isinstance(x, QPointF):
            # x is a point and y is ignored
            x, y = x.x(), x.y()

        self.x = x - (self.diameter // 2)
        self.y = y - (self.diameter // 2)

        super().setPos(self.x, self.y)

    def pos(self):
        """Return center of circle instead of top left"""

        x = self.x + (self.diameter // 2)
        y = self.y + (self.diameter // 2)

        return QPointF(x, y)