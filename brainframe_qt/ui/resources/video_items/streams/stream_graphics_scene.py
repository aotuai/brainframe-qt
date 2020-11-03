from typing import List

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsScene, QWidget

from brainframe.client.api_utils.detection_tracks import DetectionTrack
from brainframe.client.ui.resources.config import QSettingsRenderConfig
from brainframe.client.ui.resources.video_items.detections import DetectionItem
from brainframe.client.ui.resources.video_items.zone_statuses import \
    ZoneStatusItem
from brainframe.shared.constants import DEFAULT_ZONE_NAME


class StreamGraphicsScene(QGraphicsScene):
    def __init__(self, *, render_config: QSettingsRenderConfig,
                 parent: QWidget):

        super().__init__(parent)

        self.render_config = render_config

        self.current_frame = None

    def set_frame(self, *, pixmap=None, frame=None, path=None):

        if frame is not None:
            pixmap = self._get_pixmap_from_numpy_frame(frame)

        elif path is not None:
            pixmap = QPixmap(str(path))

        """Set the current frame to the given pixmap"""
        # Create new QGraphicsPixmapItem if there isn't one
        if not self.current_frame:
            current_frame_size = None
            self.current_frame = self.addPixmap(pixmap)

            # Fixes BF-319: Clicking a stream, closing it, and reopening it
            # again resulted in a stream that wasn't displayed properly. This
            # was because the resizeEvent() would be triggered before the frame
            # was set from None->'actual frame' preventing the setSceneRect()
            # from being called. The was not an issue if another stream was
            # clicked because it would then get _another_ resize event after
            # the frame was loaded because the frame size would be different.
            for view in self.views():
                # There should only ever be one, but we'll iterate to be sure
                # noinspection PyArgumentList
                view.resizeEvent()

        # Otherwise modify the existing one
        else:
            current_frame_size = self.current_frame.pixmap().size()
            self.current_frame.setPixmap(pixmap)

        # Resize if the new pixmap has a different size than before
        if current_frame_size != self.current_frame.pixmap().size():
            for view in self.views():
                # There should only ever be one, but we'll iterate to be sure
                # noinspection PyArgumentList
                view.resizeEvent()
                view.updateGeometry()

    def draw_lines(self, zone_statuses):
        # Draw all of the zones (except the default zone)
        for zone_status in zone_statuses.values():
            if zone_status.zone.name != DEFAULT_ZONE_NAME:
                if len(zone_status.zone.coords) == 2:
                    self._new_zone_status_polygon(zone_status)

    def draw_regions(self, zone_statuses):
        # Draw all of the zones (except the default zone)
        for zone_status in zone_statuses.values():
            if zone_status.zone.name != DEFAULT_ZONE_NAME:
                if len(zone_status.zone.coords) > 2:
                    self._new_zone_status_polygon(zone_status)

    def draw_detections(self, frame_tstamp: float,
                        tracks: List[DetectionTrack]):

        for track in tracks:
            detection = track.get_interpolated_detection(frame_tstamp)
            detection_item = DetectionItem(
                detection,
                track=track,
                render_config=self.render_config
            )
            self.addItem(detection_item)

    def remove_items(self, items, condition=any):
        for item in items:
            if condition is any or condition(item):
                self.removeItem(item)

    def remove_all_items(self):

        def condition(item):
            return item is not self.current_frame

        self.remove_items(self.items(), condition)

    @staticmethod
    def _get_pixmap_from_numpy_frame(frame):
        height, width, channel = frame.shape
        bytes_per_line = width * 3
        image = QImage(frame.data, width, height, bytes_per_line,
                       QImage.Format_RGB888)
        return QPixmap.fromImage(image)

    def _new_zone_status_polygon(self, zone_status):
        zone_status_item = ZoneStatusItem(
            zone_status,
            render_config=self.render_config
        )

        self.addItem(zone_status_item)

    @property
    def _item_text_size(self):
        return int(self.height() / 50)
