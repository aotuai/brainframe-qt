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
        """Formats a string in the format of
        ClassName(arg1=val, arg2=val, arg3=val)"""
        argstring = ""
        for argname, argval in self.to_dict().items():
            if len(argstring):
                argstring += ", "
            argstring += f"{argname}={argval}"
        return f"{type(self).__name__}({argstring})"

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
