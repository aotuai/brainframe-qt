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
        self.set_render_settings(detections=False, zones=False)

        self.zones: List[StreamPolygon] = []
        """List of zones"""

        # Variables related to making a new polygon
        self.unconfirmed_polygon: StreamPolygon = None
        self.max_points = None

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Called when mouse click is _released_ on Widget"""

        # Ignore mouseEvents (until new region is begun)
        if self.unconfirmed_polygon is not None:
            points = self.unconfirmed_polygon.points_list

            # If maximum points has already been reached
            if self.max_points is not None and len(points) >= self.max_points:
                return

            # Get the coordinates of the mouse press in the scene's coordinates
            click = self.mapToScene(event.pos())

            # Don't allow the user to input an invalid polygon
            if len(self.unconfirmed_polygon.polygon) > 2:
                # points = [(point.x(), point.y())
                #           for point in self.unconfirmed_polygon.polygon]
                points = self.unconfirmed_polygon.points_list
                points.append((click.x(), click.y()))
                shapely_polygon = geometry.Polygon(points)
                if not shapely_polygon.is_valid:
                    print("User tried to enter invalid point")
                    return

            # Create new circle
            circle = ClickCircle(click.x(), click.y(),
                                 diameter=10,
                                 color=Qt.red)
            self.scene_.addItem(circle)

            self.unconfirmed_polygon.insert_point(click)

            # Draw item if not already drawn
            if self.unconfirmed_polygon not in self.scene_.items():
                self.scene_.addItem(self.unconfirmed_polygon)

        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Render a line being drawn to show what the polygon will look like
        if the mouse is clicked"""

        if self.unconfirmed_polygon is None:
            return
        if len(self.unconfirmed_polygon.polygon) < 1:
            return

        points = self.unconfirmed_polygon.points_list
        if self.max_points is not None and len(points) >= self.max_points:
            return

        self.remove_items_by_type(StreamPolygon)
        move_point = self.mapToScene(event.pos())
        points.append(move_point)

        visual_polygon = StreamPolygon(points, opacity=.25)

        # Add the new polygon first, then superimpose the current polygon
        self.scene_.addItem(visual_polygon)
        self.scene_.addItem(self.unconfirmed_polygon)

    def start_new_polygon(self, max_points=None):
        self.setMouseTracking(True)  # Allow for realtime zone updating
        self.unconfirmed_polygon = StreamPolygon()
        self.max_points = max_points

    def confirm_unconfirmed_polygon(self):
        # Clear all objects that built up while making the polygon
        self.remove_items_by_type(StreamPolygon)
        self.remove_items_by_type(ClickCircle)

        # Add the green finished polygon
        self.unconfirmed_polygon.set_color(Qt.green)
        self.scene_.addItem(self.unconfirmed_polygon)

        self.zones.append(self.unconfirmed_polygon)

        ret = self.unconfirmed_polygon.polygon

        # Polygon is no longer "unconfirmed" so delete that reference
        self.unconfirmed_polygon = None
        self.max_points = None
        return ret

    def clear_unconfirmed_polygon(self):

        if self.unconfirmed_polygon is not None:
            self.scene_.removeItem(self.unconfirmed_polygon)
            self.remove_items_by_type(StreamPolygon)
            self.remove_items_by_type(ClickCircle)
            self.unconfirmed_polygon = None
            self.max_points = None
