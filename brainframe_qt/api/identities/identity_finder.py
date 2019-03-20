from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from abc import ABC, abstractmethod

from brainframe.client.api.codecs import Identity
from brainframe.client.api.api_stub import API


VECTOR = List[float]


# TODO: Use @dataclass decorator in Python3.7
class IdentityPrototype:
    """Information on a to-be-created identity, including the images and and
    vectors that should be saved under this identity.
    """

    def __init__(self):
        self.unique_name: str = None
        """The identity's unique name."""

        self.nickname: str = None
        """The identity's nickname."""

        self.images_by_class_name: Dict[str, List[Tuple[Path, bytes]]] = \
            defaultdict(list)
        """The images that should be encoded and assigned to this identity. The
        key is the class name, and the value is all images that should be
        encoded under that class name for this identity.
        """

        self.vectors_by_class_name: Dict[str, List[Tuple[Path, VECTOR]]] = \
            defaultdict(list)
        """The vectors that should be assigned to this identity. The key is the
        class name, and the value is all vectors that should be encoded under
        that class name for this identity.
        """


class IdentityFinder(ABC):
    """Describes a type that is capable of creating IdentityPrototypes from
    some source. This can be used to import identities from another format into
    BrainFrame.
    """

    @abstractmethod
    def find(self) -> List[IdentityPrototype]:
        """Finds IdentityPrototypes from some source.

        :return: Found prototypes
        """
        raise NotImplementedError


def create_identity_from_prototype(api: API, prototype: IdentityPrototype) \
        -> Identity:
    """Creates the identity and all of its encodings based on the given
    prototype.

    :param api: The API object to use when creating these identities
    :param prototype: The prototype to create from
    :return: The created identity
    """
    identity = Identity(
        unique_name=prototype.unique_name,
        nickname=prototype.nickname,
        metadata={})

    identity = api.set_identity(identity)

    for class_name, images in prototype.images_by_class_name.items():
        for image_name, image_bytes in images:
            image_id = api.new_storage_as_image(image_bytes)
            api.new_identity_image(identity.id, class_name, image_id)

    for class_name, vectors in prototype.vectors_by_class_name.items():
        for file_name, vector in vectors:
            api.new_identity_vector(identity.id, class_name, vector)

    return identity
