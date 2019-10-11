import abc
import ujson


class Codec(abc.ABC):
    """A serializable object."""

    @abc.abstractmethod
    def to_dict(self) -> dict:
        pass

    @abc.abstractstaticmethod
    def from_dict(d: dict):
        pass

    def to_json(self) -> str:
        return ujson.dumps(self.to_dict())

    @classmethod
    def from_json(cls, j: str):
        return cls.from_dict(ujson.loads(j))

    def __repr__(self):
        return str(self.to_dict())

    def __eq__(self, other):
        if type(other) is dict:
            return self.to_dict() == other

        if type(other) is not type(self):
            return NotImplemented

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        if type(other) is not type(self):
            return NotImplemented

        return self.to_dict() != other.to_dict()
