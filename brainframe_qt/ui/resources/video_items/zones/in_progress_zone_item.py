from abc import ABC, abstractmethod
from typing import List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from brainframe.api.bf_codecs import Zone

from brainframe_qt.ui.resources.config import RenderSettings
from brainframe_qt.ui.resources.video_items.base import CircleItem, \
    VideoItem
from .abstract_zone_item import AbstractZoneItem
from .zone_line_item import ZoneLineItem
from .zone_region_item import ZoneRegionItem


class InProgressZoneItem(VideoItem, ABC):

    def __init__(self, coords: List[VideoItem.PointType], *,
                 render_config: RenderSettings,
                 parent: Optional[VideoItem] = None,
                 line_style: Qt.PenStyle = Qt.SolidLine):
        super().__init__(parent=parent)

        self.coords = coords
        self.render_config = render_config

        self._line_style = line_style
        self._zone_item = self._init_zone_item()
        self._vertex_items = self._init_vertex_items()

    @property
    def current_vertices(self) -> List[VideoItem.PointType]:
        return [vertex_item.pos() for vertex_item in self._vertex_items]

    def add_vertex(self, vertex: VideoItem.PointType) -> None:
        if not self.takes_additional_points():
            raise RuntimeError("This zone item does not support adding any "
                               "more points")

        self.coords.append(vertex)

        if self._zone_item is not None:
            self.scene().removeItem(self._zone_item)
        self._zone_item = self._init_zone_item()

        vertex_item = _DraggableVertex(vertex, parent=self)
        self._vertex_items.append(vertex_item)

    def update_latest_vertex(self, vertex: VideoItem.PointType) -> None:
        """Updates the position of the latest vertex. The zone item must have
        at least one vertex added to call this method.

        :param vertex: The new position
        """
        if len(self.coords) == 0:
            raise RuntimeError("The zone item has no vertices to update")

        self.coords[-1] = vertex

        if self._zone_item is not None:
            self.scene().removeItem(self._zone_item)
        self._zone_item = self._init_zone_item()

        self.scene().removeItem(self._vertex_items[-1])
        self._vertex_items[-1] = _DraggableVertex(vertex, parent=self)

    @abstractmethod
    def is_shape_ready(self) -> bool:
        """
        :return: True if the item represents a valid zone in its current state
        """

    @abstractmethod
    def takes_additional_points(self) -> bool:
        """
        :return: True if the user can add more points to this zone item
        """

    @abstractmethod
    def _init_zone_item(self) -> Optional[AbstractZoneItem]:
        """
        :return: A zone item that can draw this zone's lines, or None if the
            zone is not ready to be drawn yet
        """

    def _init_vertex_items(self) -> List['_DraggableVertex']:
        vertex_items: List[_DraggableVertex] = []
        for coord in self.coords:
            vertex_items.append(_DraggableVertex(coord, parent=self))

        return vertex_items


class InProgressRegionItem(InProgressZoneItem):
    def is_shape_ready(self) -> bool:
        return len(self.coords) >= 3

    def takes_additional_points(self) -> bool:
        # A region zone can take an infinite amount of points
        return True

    def _init_zone_item(self) -> Optional[ZoneRegionItem]:
        if len(self.coords) < 2:
            return None
        else:
            points = list(map(list, self.coords))
            zone = Zone(name="in_progress_region", coords=points, stream_id=-1)

            return ZoneRegionItem(
                zone,
                render_config=self.render_config,
                line_style=self._line_style,
                parent=self)


class InProgressLineItem(InProgressZoneItem):
    def is_shape_ready(self) -> bool:
        return len(self.coords) == 2

    def takes_additional_points(self) -> bool:
        return len(self.coords) < 2

    def _init_zone_item(self) -> Optional[ZoneLineItem]:
        if len(self.coords) < 2:
            return None
        else:
            points = list(map(list, self.coords))
            zone = Zone(name="in_progress_line", coords=points, stream_id=-1)

            return ZoneLineItem(
                zone,
                render_config=self.render_config,
                line_style=self._line_style,
                parent=self)


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
