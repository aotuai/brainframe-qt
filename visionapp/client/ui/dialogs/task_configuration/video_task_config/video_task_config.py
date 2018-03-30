from typing import List

from PyQt5.QtCore import pyqtSignal, QPointF, Qt
from PyQt5.QtGui import QMouseEvent
from shapely import geometry

from visionapp.client.ui.resources.video_items import (
    ClickCircle,
    StreamWidget,
    StreamPolygon
)


class VideoTaskConfig(StreamWidget):

    polygon_is_valid_signal = pyqtSignal(bool)

    def __init__(self, parent=None, stream_conf=None, frame_rate=30):
        super().__init__(stream_conf, frame_rate, parent)

        self.points: List[QPointF] = []
        """List of click points. Used to draw Polygon"""

        self.zones: List[StreamPolygon] = []
        """List of zones"""

        self.unconfirmed_polygon: StreamPolygon = None

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

        # TODO: Alex: Uncomment; This won't work off the bat
        # How to reset polygon?
        # polygon = geometry.Polygon(self.unconfirmed_polygon)
        # if polygon.is_convex:
        #     # TODO: Needs to be wired to slot in TaskConfiguration widget
        #     self.polygon_is_valid_signal.emit(False)
        # else:
        #     self.polygon_is_valid_signal.emit(True)

        super().mouseReleaseEvent(event)

    def start_new_polygon(self):
        self.unconfirmed_polygon = StreamPolygon(StreamPolygon.PolygonType.zone)

    def confirm_unconfirmed_polygon(self):
        self.zones.append(self.unconfirmed_polygon)
        self.unconfirmed_polygon.set_color(Qt.green)

        ret = self.unconfirmed_polygon.polygon

        # Polygon is no longer "unconfirmed" so delete that reference
        self.unconfirmed_polygon = None

        return ret

    def clear_unconfirmed_polygon(self):

        if self.unconfirmed_polygon is not None:
            self.scene_.removeItem(self.unconfirmed_polygon)
            self.unconfirmed_polygon = None
