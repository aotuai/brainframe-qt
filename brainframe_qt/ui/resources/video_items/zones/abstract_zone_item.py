from typing import Tuple

from PyQt5.QtGui import QColor
from brainframe.api.bf_codecs import Zone

from brainframe.client.ui.resources.video_items.base import VideoItem


class AbstractZoneItem:
    BORDER_COLOR = QColor(0, 255, 125)
    BORDER_THICKNESS = 6

    def __init__(self, zone: Zone):
        self.zone = zone

    @property
    def zone_coords(self) -> Tuple[VideoItem.PointType]:
        # noinspection PyTypeChecker
        return tuple(map(tuple, self.zone.coords))

    @property
    def zone_is_line(self) -> bool:
        return len(self.zone.coords) == 2

    @property
    def zone_is_region(self) -> bool:
        return len(self.zone.coords) > 2

    @property
    def zone_name(self) -> str:
        return self.zone.name
