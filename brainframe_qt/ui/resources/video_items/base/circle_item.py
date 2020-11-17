from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtWidgets import QGraphicsEllipseItem

from .video_item import VideoItem


class CircleItem(QGraphicsEllipseItem):

    def __init__(self, position: VideoItem.PointType, *,
                 radius, parent: VideoItem, border_thickness=1,
                 color=Qt.black):
        self.radius = radius
        self.border_thickness = border_thickness
        self.color = color

        diameter = radius * 2
        super().__init__(0, 0, diameter, diameter, parent=parent)
        self.setPos(position)

        self._init_style()

    def _init_style(self):
        pen = self.pen()
        pen.setColor(self.color)
        pen.setWidth(self.border_thickness)
        self.setPen(pen)

    def setPos(self, position: VideoItem.PointType) -> None:
        """Set position relative to center of circle instead of top left"""

        position = QPointF(*position)
        position -= QPointF(self.radius, self.radius)

        super().setPos(position)

    def pos(self) -> VideoItem.PointType:
        """Return center of circle instead of top left"""

        position = super().pos()
        position += QPointF(self.radius, self.radius)

        # noinspection PyTypeChecker
        return position.x(), position.y()
