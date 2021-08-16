from typing import List, Optional

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget

from brainframe_qt.api_utils.streaming.zone_status_frame import ZoneStatusFrame
from brainframe_qt.ui.resources.video_items.base import VideoItem
from brainframe_qt.ui.resources.video_items.streams import StreamWidget

from ..core.zone import Zone
from .in_progress_zone_item import InProgressZoneItem


class VideoTaskConfig(StreamWidget):
    polygon_is_valid_signal = pyqtSignal(bool)

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)

        # Always draw regions and lines. Never draw detections.
        self.draw_regions = True
        self.draw_lines = True
        self.draw_detections = False

        self.in_progress_zone: Optional[Zone] = None
        self._in_progress_zone_item: Optional[InProgressZoneItem] = None
        self.preview_zone: Optional[Zone] = None
        self._preview_zone_item: Optional[InProgressZoneItem] = None

        # Allow for real-time zone previews
        self.setMouseTracking(True)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        click_pos = self.mapToScene(event.pos())
        click_pos = (click_pos.x(), click_pos.y())
        self._handle_click(click_pos)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        # Don't do anything if we're not currently making a zone
        if self.preview_zone is None:
            return

        # Update the preview zone if the user has the option to add more points
        if self.in_progress_zone.takes_additional_points():
            mouse_pos = self.mapToScene(event.pos())
            mouse_pos = (int(mouse_pos.x()), int(mouse_pos.y()))
            self.preview_zone.adjust_final_vertex(mouse_pos)

            self._update_zone_items()

    def _handle_click(self, click_pos: VideoItem.PointType) -> None:
        # Don't do anything if we're not currently making a zone
        if self.in_progress_zone is None:
            return

        # Don't do anything if the zone can't take any more points
        if not self.in_progress_zone.takes_additional_points():
            return

        # Make sure click will result in a valid zone
        if len(self.in_progress_zone.coords) >= 3:
            if not self.in_progress_zone.would_be_valid_zone(click_pos):
                return

        self.in_progress_zone.add_vertex(click_pos)
        self.preview_zone.add_vertex(click_pos)

        # Allow the user to confirm the zone if it's valid
        if self.in_progress_zone.is_shape_ready():
            self.polygon_is_valid_signal.emit(True)

    def on_frame(self, frame: ZoneStatusFrame) -> None:
        # Only change the video frame if we're in the process of creating a new zone
        if self.in_progress_zone is None:
            super().on_frame(frame)
        else:
            self.scene().set_frame(pixmap=frame.frame)

    def start_zone_edit(self, zone: Zone) -> None:
        # Temporarily disable region and line drawing
        self.render_config.draw_regions = False
        self.render_config.draw_lines = False

        self.scene().remove_all_items()

        self.in_progress_zone = zone.copy()
        self.preview_zone = zone.copy()
        self.preview_zone.coords.append(self.preview_zone.coords[-1])

        self._add_zone_items()

    def confirm_zone_edit(self) -> List[VideoItem.PointType]:
        zone_vertices = self.in_progress_zone.coords
        self.discard_zone_edit()

        return zone_vertices

    def discard_zone_edit(self) -> None:
        # Clear out in-progress state
        self._remove_zone_items()

        self.in_progress_zone = None
        self.preview_zone = None

        # Re-enable region and line drawing
        self.render_config.draw_regions = True
        self.render_config.draw_lines = True

    def _add_zone_items(self) -> None:
        self._in_progress_zone_item = InProgressZoneItem.from_zone(
            self.in_progress_zone, render_config=self.render_config
        )
        self._preview_zone_item = InProgressZoneItem.from_zone(
            self.preview_zone, render_config=self.render_config, line_style=Qt.DotLine
        )

        self.scene().addItem(self._in_progress_zone_item)
        self.scene().addItem(self._preview_zone_item)

    def _remove_zone_items(self) -> None:
        self.scene().removeItem(self._in_progress_zone_item)
        self.scene().removeItem(self._preview_zone_item)

        self._in_progress_zone_item = None
        self._preview_zone_item = None

    def _update_zone_items(self) -> None:
        self._in_progress_zone_item.zone = self.in_progress_zone
        self._preview_zone_item.zone = self.preview_zone

        self._in_progress_zone_item.refresh_shape()
        self._preview_zone_item.refresh_shape()
