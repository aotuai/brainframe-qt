import logging

from PyQt5.QtCore import pyqtSignal, QPointF, Qt
from PyQt5.QtGui import QMouseEvent, QColor
from shapely import geometry

from brainframe.client.api.streaming import ProcessedFrame
from brainframe.client.ui.resources.video_items import (
    ClickCircle,
    StreamWidget,
    StreamPolygon
)


class VideoTaskConfig(StreamWidget):
    polygon_is_valid_signal = pyqtSignal(bool)

    draw_detections = False
    draw_lines = True
    draw_regions = True

    def __init__(self, parent=None, stream_conf=None):
        super().__init__(stream_conf, parent)

        # Variables related to making a new polygon
        self.unconfirmed_polygon: StreamPolygon = None
        self.max_points = None

        # Set when a mousePressEvent occurs on top of a ClickCircle during
        # edits
        self.clicked_circle = None  # type: ClickCircle

    def handle_frame(self, processed_frame: ProcessedFrame,
                     remove_items=False):

        self.scene().set_frame(frame=processed_frame.frame)

        if self.unconfirmed_polygon is None:
            super().handle_frame(processed_frame)

    def mousePressEvent(self, event: QMouseEvent):
        item_at = self.itemAt(event.pos())
        if isinstance(item_at, ClickCircle):
            self.clicked_circle = self.itemAt(event.pos())

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Called when mouse click is _released_ on Widget"""

        # Don't do anything if a ClickCircle was clicked on mouse _press_
        if self.clicked_circle:
            self.clicked_circle = None
            return

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
                if not self._is_polygon_valid(points, click):
                    logging.warning("User tried to enter invalid point")
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

        mouse_pos = self.mapToScene(event.pos())
        points = self.unconfirmed_polygon.points_list

        self.scene().remove_items_by_type(StreamPolygon)

        # Draw current polygon
        self.scene().addItem(self.unconfirmed_polygon)

        if event.buttons() == Qt.LeftButton and self.clicked_circle:
            # We're dragging a circle

            # Create a temp polygon and check if it's valid after dragging
            temp_polygon = StreamPolygon(self.unconfirmed_polygon.polygon)
            temp_polygon.move_point(self.clicked_circle.pos(), mouse_pos)

            if (len(temp_polygon.polygon) > 2  # Don't check lines
                    and not self._is_polygon_valid(temp_polygon.points_list)):
                # If not valid, don't move anything
                return

                # Move polygon point and click circle
            self.unconfirmed_polygon.move_point(self.clicked_circle.pos(),
                                                mouse_pos)
            self.clicked_circle.setPos(mouse_pos)

        else:  # Nothing is being dragged.

            # Only create a preview polygon if we have more points to add
            # Otherwise, polygon drawn is what will be confirmed
            if self.max_points is None or len(points) < self.max_points:
                points.append((mouse_pos.x(), mouse_pos.y()))

            preview_polygon = StreamPolygon(
                points,
                opacity=.25,
                border_thickness=self.scene().width() / 200,
                border_color=QColor(50, 255, 50))

            # Draw preview polygon
            self.scene().addItem(preview_polygon)

    def start_new_polygon(self, max_points=None):

        self.draw_regions = False
        self.draw_lines = False

        self.scene().remove_all_items()

        self.setMouseTracking(True)  # Allow for realtime zone updating
        self.unconfirmed_polygon = StreamPolygon(
            border_thickness=self.scene().width() / 200,
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
            self.scene().remove_items_by_type(StreamPolygon)
            self.scene().remove_items_by_type(ClickCircle)
            self.unconfirmed_polygon = None
            self.max_points = None

        self.draw_regions = True
        self.draw_lines = True

    @staticmethod
    def _is_polygon_valid(point_list, new_point: QPointF = None):
        """Verify that a list of points is a valid shapely Polygon"""
        if new_point:
            if isinstance(new_point, QPointF):
                new_point = new_point.x(), new_point.y()
            point_list.append(new_point)

        shapely_polygon = geometry.Polygon(point_list)

        return shapely_polygon.is_valid
