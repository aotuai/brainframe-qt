from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


from brainframe.api import bf_codecs


@dataclass
class Zone(ABC):
    name: str
    coords: List[List[int]]

    @abstractmethod
    def is_shape_ready(self) -> bool:
        ...

    @abstractmethod
    def takes_additional_points(self) -> bool:
        ...

    def to_api_zone(self, stream_id: int) -> bf_codecs.Zone:
        return bf_codecs.Zone(
            name=self.name,
            stream_id=stream_id,
            coords=self.coords
        )


class Line(Zone):
    def is_shape_ready(self) -> bool:
        return len(self.coords) == 2

    def takes_additional_points(self) -> bool:
        return len(self.coords) < 2


class Region(Zone):
    def is_shape_ready(self) -> bool:
        return len(self.coords) == 2

    def takes_additional_points(self) -> bool:
        return True
