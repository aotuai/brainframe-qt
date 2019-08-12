from typing import List, Optional

from .base_codecs import Codec


class Encoding(Codec):
    """An encoding attached to an identity."""

    def __init__(self, *, identity_id: int,
                 class_name: str,
                 from_image: Optional[int],
                 vector: List[int],
                 id_=None):
        self.identity_id = identity_id
        self.class_name = class_name
        self.from_image = from_image
        self.vector = vector
        self.id = id_

    def to_dict(self):
        d = dict(self.__dict__)
        return d

    @staticmethod
    def from_dict(d):
        return Encoding(id_=d["id"],
                        identity_id=d["identity_id"],
                        class_name=d["class_name"],
                        from_image=d["from_image"],
                        vector=d["vector"])
