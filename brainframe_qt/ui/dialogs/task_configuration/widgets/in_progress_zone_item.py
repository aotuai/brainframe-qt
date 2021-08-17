from abc import ABC, abstractmethod
from typing import List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from brainframe.api import bf_codecs

from brainframe_qt.ui.resources.config import RenderSettings
from brainframe_qt.ui.resources.video_items.base import CircleItem, VideoItem
from brainframe_qt.ui.resources.video_items.zones import ZoneLineItem, ZoneRegionItem

from ..core.zone import Line, Region, Zone


class InProgressZoneItem(VideoItem, ABC):

    _DEFAULT_LINE_STYLE: Qt.PenStyle = Qt.SolidLine

    def __init__(self, zone: Zone, *,
                 render_config: RenderSettings,
                 parent: Optional[VideoItem] = None,
                 line_style: Qt.PenStyle = _DEFAULT_LINE_STYLE):
        super().__init__(parent=parent)

        self.zone = zone
        self.render_config = render_config

        self._line_style = line_style

        self._zone_item = self._init_zone_item()
        self._vertex_items = self._init_vertex_items()

    @classmethod
    def from_zone(
        cls, zone: Zone, *,
        render_config: RenderSettings, line_style: Qt.PenStyle = _DEFAULT_LINE_STYLE
    ) -> "InProgressZoneItem":
        if isinstance(zone, Region):
            return InProgressRegionItem(
                zone,
                render_config=render_config,
                line_style=line_style,
            )
        elif isinstance(zone, Line):
            return InProgressLineItem(
                zone,
                render_config=render_config,
                line_style=line_style
            )

    @property
    def current_vertices(self) -> List[VideoItem.PointType]:
        return [vertex_item.pos() for vertex_item in self._vertex_items]

    def add_vertex(self, vertex: VideoItem.PointType) -> None:
        if not self.zone.takes_additional_points():
            raise RuntimeError("This zone item does not support adding any "
                               "more points")

        self.zone.coords.append(vertex)

        self.refresh_shape()

        vertex_item = _DraggableVertex(vertex, parent=self)
        self._vertex_items.append(vertex_item)

    def refresh_shape(self) -> None:
        if self._zone_item is not None and self.scene() is not None:
            self.scene().removeItem(self._zone_item)
            for item in self._vertex_items:
                self.scene().removeItem(item)

        self._zone_item = self._init_zone_item()
        if self._zone_item is not None:
            self._vertex_items = self._init_vertex_items()

    @abstractmethod
    def _init_zone_item(self) -> Optional["InProgressZoneItem"]:
        """
        :return: A zone item that can draw this zone's lines, or None if the
            zone is not ready to be drawn yet
        """

    def _init_vertex_items(self) -> List['_DraggableVertex']:
        assert self.zone.coords is not None

        vertex_items: List[_DraggableVertex] = []
        for coord in self.zone.coords:
            vertex_items.append(_DraggableVertex(coord, parent=self))

        return vertex_items


class InProgressRegionItem(InProgressZoneItem):
    def _init_zone_item(self) -> Optional[ZoneRegionItem]:
        if len(self.zone.coords) < 2:
            return None

        points = list(map(list, self.zone.coords))
        zone = bf_codecs.Zone(name="in_progress_zone", coords=points, stream_id=-1)

        return ZoneRegionItem(
            zone=zone,
            render_config=self.render_config,
            line_style=self._line_style,
            parent=self
        )


class InProgressLineItem(InProgressZoneItem):
    def _init_zone_item(self) -> Optional[ZoneLineItem]:
        if len(self.zone.coords) < 2:
            return None

        points = list(map(list, self.zone.coords))
        zone = bf_codecs.Zone(name="in_progress_line", coords=points, stream_id=-1)

        return ZoneLineItem(
            zone=zone,
            render_config=self.render_config,
            line_style=self._line_style,
            parent=self
        )


class _DraggableVertex(CircleItem):
    # TODO: Tie to size of scene
    DEFAULT_RADIUS = 10
    DEFAULT_BORDER_THICKNESS = 5
    DEFAULT_COLOR = QColor(200, 50, 50)

    def __init__(self, position: VideoItem.PointType, *, parent: VideoItem):
        super().__init__(position, color=self.DEFAULT_COLOR,
                         radius=self.DEFAULT_RADIUS,
                         border_thickness=self.DEFAULT_BORDER_THICKNESS,
                         parent=parent)

        # self.setFlag(self.ItemIsSelectable, True)
        # self.setFlag(self.ItemIsMovable, True)

    # def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
    #     event.ignore()
    #     super().mouseMoveEvent(event)
    #
    # def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
    #     event.ignore()
    #     super().mouseMoveEvent(event)