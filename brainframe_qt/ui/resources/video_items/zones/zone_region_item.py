from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from brainframe.api.bf_codecs import Zone

from brainframe_qt.ui.resources.config import QSettingsRenderConfig
from brainframe_qt.ui.resources.video_items.base import PolygonItem, \
    VideoItem
from .abstract_zone_item import AbstractZoneItem


class ZoneRegionItem(AbstractZoneItem, PolygonItem):

    def __init__(self, zone: Zone, *,
                 render_config: QSettingsRenderConfig,
                 parent: VideoItem,
                 color: QColor = AbstractZoneItem.BORDER_COLOR,
                 thickness: int = AbstractZoneItem.BORDER_THICKNESS,
                 line_style: Qt.PenStyle = Qt.SolidLine):
        self.color = color
        self.thickness = thickness
        self.line_style = line_style

        AbstractZoneItem.__init__(self, zone)
        PolygonItem.__init__(self, zone.coords, border_color=color,
                             parent=parent)

    def _init_style(self):
        super()._init_style()

        self.border_linetype = self.line_style
        self.border_thickness = self.thickness
