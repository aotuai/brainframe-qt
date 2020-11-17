from abc import ABC, abstractmethod
from typing import List, Type

from .activities import ClientActivity


class ClientExtension(ABC):

    @abstractmethod
    def version(self) -> str:
        ...

    @staticmethod
    @abstractmethod
    def activities() -> List[Type[ClientActivity]]:
        ...
