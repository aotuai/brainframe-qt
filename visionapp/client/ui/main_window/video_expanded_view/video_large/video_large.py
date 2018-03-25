from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QPen
from PyQt5.QtWidgets import QGraphicsEllipseItem

from visionapp.client.ui.resources.stream_widget import StreamWidget


class VideoLarge(StreamWidget):

    def __init__(self, parent=None, stream_conf=None, frame_rate=30):

        super().__init__(stream_conf, frame_rate, parent)

    def mouseReleaseEvent(self, event: QMouseEvent):

        click = self.mapToScene(event.pos())

        print(event.pos(), click)

        circle = QGraphicsEllipseItem(click.x() - 5, click.y() - 5,
                                      10, 10)
        pen = circle.pen()
        pen.setColor(Qt.red)
        circle.setPen(pen)

        self.scene_.addItem(circle)

        super().mouseReleaseEvent(event)