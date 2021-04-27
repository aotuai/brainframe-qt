from typing import Optional, Union

from brainframe.api.bf_codecs import ZoneStatus

from brainframe_qt.ui.resources.config import RenderSettings
from brainframe_qt.ui.resources.video_items.base import VideoItem
from brainframe_qt.ui.resources.video_items.zones import ZoneLineItem, \
    ZoneRegionItem
from .zone_status_label_item import ZoneStatusLabelItem
from .zone_status_line_item import ZoneStatusLineItem
from .zone_status_region_item import ZoneStatusRegionItem


class ZoneStatusItem(VideoItem):

    def __init__(self, zone_status: ZoneStatus, *,
                 render_config: RenderSettings,
                 parent: Optional[VideoItem] = None):

        super().__init__(parent=parent)

        self.zone_status = zone_status
        self.render_config = render_config

        self.zone_item: Union[ZoneRegionItem, ZoneLineItem]
        if len(self.zone_status.zone.coords) == 2:
            self.zone_item = self._init_line_line_item()
        else:
            self.zone_item = self._init_region_polygon_item()
        self.zone_status_label_item = self._init_zone_status_label_item()

    def _init_region_polygon_item(self) -> ZoneRegionItem:
        region_polygon_item = ZoneStatusRegionItem(
            self.zone_status,
            render_config=self.render_config,
            parent=self
        )

        return region_polygon_item

    def _init_line_line_item(self) -> ZoneLineItem:
        line_line_item = ZoneStatusLineItem(
            self.zone_status,
            render_config=self.render_config,
            parent=self,
        )

        return line_line_item

    def _init_zone_status_label_item(self) -> ZoneStatusLabelItem:
        zone_status_label_item = ZoneStatusLabelItem(
            self.zone_status,
            render_config=self.render_config,
            parent=self
        )

        return zone_status_label_item

    @property
    def is_alerting(self) -> bool:
        return bool(self.zone_status.alerts)
