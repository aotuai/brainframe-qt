from enum import Enum, auto
from typing import List, Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from shapely import geometry

from brainframe.client.ui.resources.video_items.base import VideoItem
from brainframe.client.ui.resources.video_items.stream_widget import \
    StreamWidget
from brainframe.client.ui.resources.video_items.zones import \
    InProgressLineItem, InProgressRegionItem, InProgressZoneItem


class VideoTaskConfig(StreamWidget):
    polygon_is_valid_signal = pyqtSignal(bool)

    class InProgressZoneType(Enum):
        REGION = auto()
        LINE = auto()

    def __init__(self, parent=None, stream_conf=None):
        super().__init__(stream_conf, parent)

        # Allow for real-time zone previews
        self.setMouseTracking(True)

        # Always draw regions and lines. Never draw detections.
        self.render_config.draw_regions = True
        self.render_config.draw_lines = True
        self.render_config.draw_detections = False

        self.in_progress_zone: Optional[InProgressZoneItem] = None
        """Displays to the user a zone with all the points they've chosen,
        before the whole zone is confirmed
        """
        self.preview_zone: Optional[InProgressZoneItem] = None
        """Displays to the user a zone with all the points they've chosen as
        well as a point following the mouse cursor. This gives the user a
        preview of what the zone would look like if they click.
        """

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        click_pos = self.mapToScene(event.pos())
        click_pos = (click_pos.x(), click_pos.y())
        self._handle_click(click_pos)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        # Don't do anything if we're not currently making a zone
        if self.preview_zone is None:
            return

        # Update the preview zone if the user has the option to add more points
        if self.in_progress_zone.takes_additional_points():
            mouse_pos = self.mapToScene(event.pos())
            mouse_pos = (mouse_pos.x(), mouse_pos.y())
            self.preview_zone.update_latest_vertex(mouse_pos)

    def _handle_click(self, click_pos: VideoItem.PointType) -> None:
        # Don't do anything if we're not currently making a zone
        if self.in_progress_zone is None:
            return

        # Don't do anything if the zone can't take any more points
        if not self.in_progress_zone.takes_additional_points():
            return

        vertices = self.in_progress_zone.current_vertices

        # Make sure click will result in a valid zone
        if len(vertices) >= 3:
            potential_vertices = vertices + [click_pos]
            if not self._is_valid_polygon(potential_vertices):
                return

        # Add point to in-progress zone
        self.in_progress_zone.add_vertex(click_pos)
        # Add a new point to the preview zone, if a new point can be created
        if self.in_progress_zone.takes_additional_points():
            self.preview_zone.add_vertex(click_pos)

        # Allow the user to confirm the zone if it's valid
        if self.in_progress_zone.is_shape_ready():
            self.polygon_is_valid_signal.emit(True)

    def handle_frame(self):
        # Only change the video frame if we're in the process of creating a new
        # zone
        if self.in_progress_zone is None:
            super().handle_frame()
        else:
            processed_frame = self.stream_reader.latest_processed_frame
            self.scene().set_frame(frame=processed_frame.frame)

    def start_new_zone(self, zone_type: InProgressZoneType) -> None:
        # Temporarily disable region and line drawing
        self.render_config.draw_regions = False
        self.render_config.draw_lines = False

        self.scene().remove_all_items()

        if zone_type is self.InProgressZoneType.LINE:
            self.in_progress_zone = InProgressLineItem(
                coords=[],
                render_config=self.render_config)
            self.preview_zone = InProgressLineItem(
                coords=[],
                render_config=self.render_config,
                line_style=Qt.DotLine)
        elif zone_type is self.InProgressZoneType.REGION:
            self.in_progress_zone = InProgressRegionItem(
                coords=[],
                render_config=self.render_config)
            self.preview_zone = InProgressRegionItem(
                coords=[],
                render_config=self.render_config,
                line_style=Qt.DotLine)
        else:
            raise NotImplementedError(f"Unknown zone type: {zone_type}")

        # Add the first vertex to the preview zone
        self.preview_zone.add_vertex((0.0, 0.0))

        self.scene().addItem(self.in_progress_zone)
        self.scene().addItem(self.preview_zone)

    def confirm_new_zone(self) -> List[VideoItem.PointType]:
        zone_vertices = self.in_progress_zone.current_vertices
        self.discard_new_zone()

        return zone_vertices

    def discard_new_zone(self) -> None:
        # Re-enable region and line drawing
        self.render_config.draw_regions = True
        self.render_config.draw_lines = True

        # Clear out in-progress state
        self.scene().removeItem(self.in_progress_zone)
        self.scene().removeItem(self.preview_zone)
        self.in_progress_zone = None
        self.preview_zone = None

    @staticmethod
    def _is_valid_polygon(vertices: List[VideoItem.PointType]) -> bool:
        shapely_polygon = geometry.Polygon(vertices)
        return shapely_polygon.is_valid
