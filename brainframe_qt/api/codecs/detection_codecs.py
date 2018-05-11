from .base_codecs import Codec


class Detection(Codec):
    """A detected object. It can have 'children', for example, a "person" can
    have a "face" object as a child. It can also own several Attributes. For
    example, a "person" can exhibit a behaviour. A Face can have a gender.
    """

    def __init__(self, *, class_name, rect, children, attributes):
        self.class_name = class_name
        self.rect = rect
        self.children = children
        self.attributes = attributes

    def to_dict(self):
        d = dict(self.__dict__)
        d["children"] = [Detection.to_dict(det) for det in self.children]
        d["attributes"] = [Attribute.to_dict(att) for att in self.attributes]
        return d

    @property
    def height(self):
        return self.rect[3] - self.rect[1]

    @property
    def width(self):
        return self.rect[2] - self.rect[0]

    @property
    def coords(self):
        """Conveniently return a list of coordinates, polygon style"""
        return [(self.rect[0], self.rect[1]),
                (self.rect[2], self.rect[1]),
                (self.rect[2], self.rect[3]),
                (self.rect[0], self.rect[3])]

    @staticmethod
    def from_dict(d):
        children = [Detection.from_dict(det) for det in d["children"]]
        attributes = [Attribute.from_dict(att) for att in d["attributes"]]
        return Detection(class_name=d["class_name"],
                         rect=d["rect"],
                         children=children,
                         attributes=attributes)


class Attribute(Codec):
    """This holds an attribute of a detection. These should _not_ be made
    on the client side
    """

    def __init__(self, *, category=None, value=None):
        self.category = category
        self.value = value

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Attribute(category=d["category"],
                         value=d["value"])


class Identity(Codec):
    """A specific, recognizable object or person."""

    def __init__(self, *, id_, name, class_name, metadata):
        self.id = id_
        """A unique identifier."""

        self.name = name
        """The name of the identified detection."""

        self.class_name = class_name
        """The name of the class that this detection is of."""

        self.metadata = metadata
        """Any additional user-defined information about the identity."""

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Identity(
            id_=d["id"],
            name=d["name"],
            class_name=d["class_name"],
            metadata=d["metadata"])
