from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QGraphicsScene
from brainframe.shared.constants import DEFAULT_ZONE_NAME

from .stream_detections import DetectionPolygon, ZoneStatusPolygon


class StreamGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):

        super().__init__(parent)

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
        for zone_status in zone_statuses:
            if zone_status.zone.name != DEFAULT_ZONE_NAME:
                if len(zone_status.zone.coords) == 2:
                    self._new_zone_status_polygon(zone_status)

    def draw_regions(self, zone_statuses):
        # Draw all of the zones (except the default zone)
        for zone_status in zone_statuses:
            if zone_status.zone.name != DEFAULT_ZONE_NAME:
                if len(zone_status.zone.coords) > 2:
                    self._new_zone_status_polygon(zone_status)

    def draw_detections(self, zone_statuses, *, use_bounding_boxes=True,
                        show_labels=True, show_attributes=True):

        screen_zone_status = None  # The zone with all detections in it

        # Get attributes of interest
        for zone_status in zone_statuses:
            if zone_status.zone.name == DEFAULT_ZONE_NAME:
                screen_zone_status = zone_status

        # If we don't have a screen zone status
        if not screen_zone_status:
            # But we do have a other zone statuses
            if zone_statuses:
                # We have a problem
                raise ValueError(
                    "A packet of ZoneStatuses must always include"
                    " one with the name 'Screen'")
            # Otherwise we can assume the stream is still initializing
            return

        for detection in screen_zone_status.detections:
            # Draw the detection on the screen
            polygon = DetectionPolygon(
                detection,
                text_size=self._item_text_size,
                seconds_old=0)  # Fading is currently disabled
            self.addItem(polygon)

    def remove_all_items(self):
        for item in self.items():
            # Ignore the frame pixmap
            if item is self.current_frame:
                continue
            self.removeItem(item)

    def remove_detections(self):
        detection_polygons = self._get_items_by_type(DetectionPolygon)

        for detection_polygon in detection_polygons:
            self.removeItem(detection_polygon)

    def remove_regions(self):
        region_polygons = self._get_items_by_type(ZoneStatusPolygon)

        for region_polygon in region_polygons:
            self.removeItem(region_polygon)

    def remove_lines(self):
        region_polygons = self._get_items_by_type(ZoneStatusPolygon)

        for region_polygon in region_polygons:
            if len(region_polygon.polygon) == 2:
                self.removeItem(region_polygon)

    def remove_zones(self):
        region_polygons = self._get_items_by_type(ZoneStatusPolygon)

        for region_polygon in region_polygons:
            if len(region_polygon.polygon) > 2:
                self.removeItem(region_polygon)

    def _get_items_by_type(self, item_type):
        items = self.items()
        return filter(lambda item: type(item) == item_type, items)

    @staticmethod
    def _get_pixmap_from_numpy_frame(frame):
        height, width, channel = frame.shape
        bytes_per_line = width * 3
        image = QImage(frame.data, width, height, bytes_per_line,
                       QImage.Format_RGB888)
        return QPixmap.fromImage(image)

    def _new_zone_status_polygon(self, zone_status):
        # Border thickness as % of screen size
        border = self.width() / 200
        polygon = ZoneStatusPolygon(
            zone_status,
            text_size=self._item_text_size,
            border_thickness=border
        )

        self.addItem(polygon)

    @property
    def _item_text_size(self):
        return int(self.height() / 50)
