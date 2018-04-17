from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsEllipseItem


class ClickCircle(QGraphicsEllipseItem):
    """Debug class used for showing mouse clicks on video"""

    def __init__(self, x, y, *,
                 diameter=None, radius=None, border_thickness=1,
                 color=Qt.black, parent=None):
        if radius is not None:
            diameter = radius * 2
        self.diameter = diameter

        self.x = x - (diameter // 2)
        self.y = y - (diameter // 2)

        self.color = color

        super().__init__(self.x, self.y, diameter, diameter, parent=parent)

        pen = self.pen()
        pen.setColor(color)
        pen.setWidth(border_thickness)
        self.setPen(pen)
