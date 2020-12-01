from typing import Tuple

from PyQt5.QtGui import QColor
from brainframe.api.bf_codecs import ZoneStatus

from brainframe_qt.ui.resources.video_items.base import VideoItem
from brainframe_qt.ui.resources.video_items.zones import AbstractZoneItem


class AbstractZoneStatusItem:
    NORMAL_COLOR = AbstractZoneItem.BORDER_COLOR
    ALERTING_COLOR = QColor(255, 125, 0)
    BORDER_THICKNESS = AbstractZoneItem.BORDER_THICKNESS

    def __init__(self, zone_status: ZoneStatus):
        self.zone_status = zone_status

    @property
    def is_alert_active(self) -> bool:
        return bool(self.zone_status.alerts)

    @property
    def is_detection_within(self) -> bool:
        return bool(self.zone_status.detection_within_counts)

    @property
    def is_detection_entering(self) -> bool:
        return bool(self.zone_status.entering)

    @property
    def is_detection_exiting(self) -> bool:
        return bool(self.zone_status.exiting)

    @property
    def line_color(self) -> QColor:
        return self.ALERTING_COLOR \
            if self.is_alert_active \
            else self.NORMAL_COLOR

    @property
    def should_highlight(self) -> bool:
        if self.is_alert_active:
            return True
        if self.is_detection_within:
            return True
        if self.is_detection_entering:
            return True
        if self.is_detection_exiting:
            return True

        return False

    @property
    def zone_coords(self) -> Tuple[VideoItem.PointType]:
        # noinspection PyTypeChecker
        return tuple(map(tuple, self.zone_status.zone.coords))

    @property
    def zone_is_line(self) -> bool:
        return len(self.zone_status.zone.coords) == 2

    @property
    def zone_is_region(self) -> bool:
        return len(self.zone_status.zone.coords) > 2

    @property
    def zone_name(self) -> str:
        return self.zone_status.zone.name
