from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from brainframe.api import bf_codecs


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
    def is_shape_ready(self) -> bool:
        ...

    @abstractmethod
    def takes_additional_points(self) -> bool:
        ...

    def to_api_zone(self, stream_id: int) -> bf_codecs.Zone:
        assert self.name is not None

        # BrainFrame uses a list of lists
        coords = [] if self.coords is None else list(map(list, self.coords))

        return bf_codecs.Zone(
            name=self.name,
            stream_id=stream_id,
            coords=coords,
        )

    @classmethod
    def from_api_zone(cls, zone: bf_codecs.Zone) -> "Zone":
        if zone.name == bf_codecs.Zone.FULL_FRAME_ZONE_NAME or len(zone.coords) > 2:
            return Region.from_api_region(zone)
        else:
            return Line.from_api_line(zone)


class Line(Zone):
    def is_shape_ready(self) -> bool:
        return len(self.coords) == 2

    def takes_additional_points(self) -> bool:
        return len(self.coords) < 2

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
    def is_shape_ready(self) -> bool:
        return len(self.coords) == 2

    def takes_additional_points(self) -> bool:
        return True

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
