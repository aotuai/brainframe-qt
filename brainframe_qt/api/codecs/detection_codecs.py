from typing import Optional
import uuid

from .base_codecs import Codec


class Detection(Codec):
    """A detected object. It can have 'children', for example, a "person" can
    have a "face" object as a child. It can also own several Attributes. For
    example, a "person" can exhibit a behaviour. A Face can have a gender.
    """

    def __init__(self, *, class_name, coords, children, attributes,
                 with_identity, extra_data, track_id):
        self.class_name = class_name
        self.coords = coords
        self.children = children
        self.attributes = attributes
        self.with_identity: Optional[Identity] = with_identity
        self.extra_data = extra_data
        self.track_id: Optional[uuid.UUID] = track_id

    def to_dict(self):
        d = dict(self.__dict__)
        if self.with_identity:
            d["with_identity"] = Identity.to_dict(d["with_identity"])
        if self.track_id:
            d["track_id"] = str(self.track_id)
        else:
            d["track_id"] = None
        d["children"] = [Detection.to_dict(det) for det in self.children]
        d["attributes"] = [Attribute.to_dict(att) for att in self.attributes]
        return d

    @staticmethod
    def from_dict(d):
        with_identity = None
        if d["with_identity"]:
            with_identity = Identity.from_dict(d["with_identity"])
        track_id = None

        if d["track_id"]:
            track_id = uuid.UUID(d["track_id"])

        children = [Detection.from_dict(det) for det in d["children"]]
        attributes = [Attribute.from_dict(att) for att in d["attributes"]]
        return Detection(class_name=d["class_name"],
                         coords=d["coords"],
                         children=children,
                         attributes=attributes,
                         with_identity=with_identity,
                         extra_data=d["extra_data"],
                         track_id=track_id)


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

    def __init__(self, *, unique_name, nickname, metadata=None, id_=None):
        self.unique_name = unique_name
        """The unique id of the identified detection.
        
        Not to be confused with the id_ field of the object which is a field
        used by the database.
        """

        self.nickname = nickname
        """A display name for the identity which may not be unique, like a
        person's name.
        """

        self.metadata = {} if metadata is None else metadata
        """Any additional user-defined information about the identity."""

        self.id = id_
        """A unique identifier."""

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(d):
        return Identity(
            id_=d["id"],
            unique_name=d["unique_name"],
            nickname=d["nickname"],
            metadata=d["metadata"])
