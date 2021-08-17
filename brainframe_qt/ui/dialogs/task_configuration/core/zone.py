from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, TypeVar

from brainframe.api import bf_codecs
from shapely import geometry

T = TypeVar("T")


@dataclass
class Zone(ABC):
    coords: Optional[List[Tuple[int, int]]]
    """Coordinates of the endpoints/vertices of the Zone. Top left of frame is (0, 0)
    
    The full-frame region has no coords
    """

    name: Optional[str] = None
    """The name of the Zone, if it has one"""

    id: Optional[int] = None
    """The id of the Zone known by the BrainFrame backend"""

    alarms: List[bf_codecs.ZoneAlarm] = field(default_factory=list)
    """A list of Alarms that the Zone holds"""

    @abstractmethod
    def copy(self: T) -> T:
        """Deep copy"""

    @abstractmethod
    def is_shape_ready(self) -> bool:
        """Whether this type of Zone has enough points to be considered complete"""

    @abstractmethod
    def takes_additional_points(self) -> bool:
        """Whether more points can be added to this type of Zone"""

    @abstractmethod
    def would_be_valid_zone(self, new_vertex: Tuple[int, int]) -> bool:
        """Whether the addition of new_vertex to the zone would result in a valid
        zone"""

    def add_vertex(self, vertex: Tuple[int, int]) -> None:
        if self.coords is None:
            message = (
                "Zone.coords is None. Most likely attempting to add vertex to "
                "full-frame Zone."
            )
            raise RuntimeError(message)

        assert self.coords is not None
        self.coords.append(vertex)

    def adjust_final_vertex(self, vertex: Tuple[int, int]) -> None:
        if self.coords is None:
            message = (
                "Zone.coords is None. Most likely attempting to adjust vertices on "
                "full-frame Zone."
            )
            raise RuntimeError(message)
        if len(self.coords) == 0:
            raise RuntimeError("Zone.coords is empty. No vertices to adjust.")

        self.coords[-1] = vertex

    def to_api_zone(self, stream_id: int) -> bf_codecs.Zone:
        if self.name is None:
            raise RuntimeError("Zone name is None. Cannot create API Zone codec.")

        # BrainFrame uses a list of lists
        coords = [] if self.coords is None else list(map(list, self.coords))

        return bf_codecs.Zone(
            name=self.name,
            stream_id=stream_id,
            coords=coords,
            alarms=self.alarms,
            id=self.id
        )

    @classmethod
    def from_api_zone(cls, zone: bf_codecs.Zone) -> "Zone":
        if zone.name == bf_codecs.Zone.FULL_FRAME_ZONE_NAME or len(zone.coords) > 2:
            return Region.from_api_region(zone)
        else:
            return Line.from_api_line(zone)


class Line(Zone):
    def copy(self) -> "Line":
        return Line(
            coords=self.coords.copy(),
            name=self.name,
            id=self.id,
            alarms=self.alarms.copy()
        )

    def is_shape_ready(self) -> bool:
        return len(self.coords) == 2

    def takes_additional_points(self) -> bool:
        return len(self.coords) < 2

    def would_be_valid_zone(self, new_vertex: Tuple[int, int]) -> bool:
        return True

    @classmethod
    def from_api_line(cls, zone: bf_codecs.Zone) -> "Line":
        # BrainFrame uses a list of lists
        coords = list(map(tuple, zone.coords))

        return cls(
            coords=coords,
            name=zone.name,
            id=zone.id,
            alarms=zone.alarms,
        )


class Region(Zone):
    def copy(self) -> "Region":
        coords = None if self.coords is None else self.coords.copy()

        return Region(
            coords=coords,
            name=self.name,
            id=self.id,
            alarms=self.alarms.copy()
        )

    def is_shape_ready(self) -> bool:
        return len(self.coords) >= 3

    def takes_additional_points(self) -> bool:
        return True

    def would_be_valid_zone(self, new_vertex: Tuple[int, int]) -> bool:
        new_coords = self.coords + [new_vertex]
        shapely_polygon = geometry.Polygon(new_coords)
        return shapely_polygon.is_valid

    @classmethod
    def from_api_region(cls, zone: bf_codecs.Zone) -> "Region":
        # BrainFrame uses a list of lists
        coords = None if zone.coords is None else list(map(tuple, zone.coords))

        return cls(
            coords=coords,
            name=zone.name,
            id=zone.id,
            alarms=zone.alarms,
        )
