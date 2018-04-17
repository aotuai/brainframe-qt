from PyQt5.QtCore import pyqtSignal, QPointF, Qt
from PyQt5.QtGui import QMouseEvent, QColor
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
        self.set_render_settings(detections=False, zones=True)
        
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
                                 diameter=self.scene().width() / 50,
                                 border_thickness=self.scene().width() / 100,
                                 color=QColor(200, 50, 50))
            self.scene().addItem(circle)
            circle.setZValue(self.unconfirmed_polygon.zValue() + 1)

            self.unconfirmed_polygon.insert_point(click)

            # Draw item if not already drawn
            if self.unconfirmed_polygon not in self.scene().items():
                self.scene().addItem(self.unconfirmed_polygon)

        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Render a line being drawn to show what the polygon will look like
        if the mouse is clicked"""

        if self.unconfirmed_polygon is None:
            return
        if len(self.unconfirmed_polygon.polygon) < 1:
            return
        #
        # if event.buttons() == Qt.LeftButton:
        #     print("Left")

        points = self.unconfirmed_polygon.points_list
        if self.max_points is not None and len(points) >= self.max_points:
            return

        self.remove_items_by_type(StreamPolygon)
        move_point = self.mapToScene(event.pos())
        points.append(move_point)

        preview_polygon = StreamPolygon(points,
                                        opacity=.25,
                                        border_thickness=self.scene().width() / 100,
                                        border_color=QColor(50, 255, 50))

        # Add the new polygon first, then superimpose the current polygon
        self.scene().addItem(preview_polygon)
        self.scene().addItem(self.unconfirmed_polygon)

    def start_new_polygon(self, max_points=None):
        self.set_render_settings(zones=False)
        self.setMouseTracking(True)  # Allow for realtime zone updating
        self.unconfirmed_polygon = StreamPolygon(
            border_thickness=self.scene().width() / 100,
            border_color=QColor(50, 255, 50))
        self.max_points = max_points

    def confirm_unconfirmed_polygon(self):
        # Clear all objects that built up while making the polygon
        new_polygon = self.unconfirmed_polygon.polygon
        self.clean_up()
        return new_polygon

    def clean_up(self):
        """Return the widget back to the normal mode, where it is ready to start
        creating a new polygon"""
        if self.unconfirmed_polygon is not None:
            self.scene().removeItem(self.unconfirmed_polygon)
            self.remove_items_by_type(StreamPolygon)
            self.remove_items_by_type(ClickCircle)
            self.unconfirmed_polygon = None
            self.max_points = None
        self.set_render_settings(zones=True)