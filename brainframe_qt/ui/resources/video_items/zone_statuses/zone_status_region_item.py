from PyQt5.QtCore import Qt
from brainframe.api.bf_codecs import ZoneStatus

from brainframe.client.ui.resources.config import QSettingsRenderConfig
from brainframe.client.ui.resources.video_items.base import VideoItem
from brainframe.client.ui.resources.video_items.zones import ZoneRegionItem
from .abstract_zone_status_item import AbstractZoneStatusItem


class ZoneStatusRegionItem(AbstractZoneStatusItem, ZoneRegionItem):

    def __init__(self, zone_status: ZoneStatus, *,
                 render_config: QSettingsRenderConfig, parent: VideoItem):
        AbstractZoneStatusItem.__init__(self, zone_status)
        ZoneRegionItem.__init__(self, zone_status.zone, color=self.line_color,
                                thickness=self.BORDER_THICKNESS,
                                line_style=Qt.DotLine,
                                render_config=render_config, parent=parent)

        self._init_style()

    def _init_style(self) -> None:
        super()._init_style()
        if not self.should_highlight:
            self.setOpacity(0.3)
