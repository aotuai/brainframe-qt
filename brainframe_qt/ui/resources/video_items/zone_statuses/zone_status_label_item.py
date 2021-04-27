from typing import Optional

import math
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication
from brainframe.api.bf_codecs import ZoneStatus

from brainframe_qt.ui.resources.config import RenderSettings
from brainframe_qt.ui.resources.video_items.base import LabelItem, \
    VideoItem
from .abstract_zone_status_item import AbstractZoneStatusItem


class ZoneStatusLabelItem(AbstractZoneStatusItem, LabelItem):
    NORMAL_COLOR = QColor(0, 255, 125)
    ALERTING_COLOR = QColor(255, 125, 0)

    def __init__(self, zone_status: ZoneStatus, *,
                 render_config: RenderSettings, parent: VideoItem):
        AbstractZoneStatusItem.__init__(self, zone_status)
        LabelItem.__init__(self, self.text, self._zone_pos,
                           color=self._background_color,
                           parent=parent)

        self.render_config = render_config

    @property
    def text(self) -> str:

        text_items = [
            self.zone_name,
        ]

        if self.zone_is_line:
            text_items.append(self._total_entered_text)
            text_items.append(self._total_exited_text)

        text_items.append(self._total_within_text)
        text_items.append(self._alerting_text)

        return "\n".join(filter(None.__ne__, text_items))

    @property
    def _background_color(self) -> QColor:
        return self.ALERTING_COLOR \
            if self.is_alert_active \
            else self.NORMAL_COLOR

    @property
    def _zone_pos(self) -> VideoItem.PointType:
        # Find the top-left most point of the zone
        sorted_coords = sorted(self.zone_coords,
                               key=lambda pt: math.hypot(*pt))

        return sorted_coords[0]

    @property
    def _total_entered_text(self) -> Optional[str]:
        entered_counts = self.zone_status.total_entered
        if not entered_counts:
            return None

        entered_text = QApplication.translate("ZoneStatusLabelItem",
                                              "Entering: ")
        count_text = self._count_dict_to_str(entered_counts)
        if not count_text:
            return None

        return f"{entered_text}\n" \
               f"{count_text}"

    @property
    def _total_exited_text(self) -> Optional[str]:
        exited_counts = self.zone_status.total_exited
        if not exited_counts:
            return None

        exited_text = QApplication.translate("ZoneStatusLabelItem",
                                             "Exiting: ")
        count_text = self._count_dict_to_str(exited_counts)
        if not count_text:
            return None

        return f"{exited_text}\n" \
               f"{count_text}"

    @property
    def _total_within_text(self) -> Optional[str]:
        within_counts = self.zone_status.detection_within_counts
        if not within_counts:
            return None

        within_text = QApplication.translate("ZoneStatusLabelItem", "Within: ")
        count_text = self._count_dict_to_str(within_counts)
        if not count_text:
            return None

        return f"{within_text}\n" \
               f"{count_text}"

    @property
    def _alerting_text(self) -> Optional[str]:
        if not self.zone_status.alerts:
            return None

        return QApplication.translate("ZoneStatusLabelItem", "Alert!")

    @staticmethod
    def _count_dict_to_str(count_dict: dict) -> str:
        sorted_dict = sorted(count_dict.items())

        counted_strings = (f"{count} {class_name}{'s' * bool(count - 1)}"
                           for class_name, count in sorted_dict
                           if count > 0)

        counted_str = "\n".join(counted_strings)

        return counted_str
