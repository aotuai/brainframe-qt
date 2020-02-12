from typing import Optional

from .base_codecs import Codec
from brainframe.shared import codec_enums


class User(Codec):
    """Contains information on a user."""

    RoleType = codec_enums.RoleType

    def __init__(self, *, username: str,
                 password: Optional[str],
                 role: RoleType,
                 id_=None):
        self.username = username
        self.password = password
        """This field will be None when retrieving users from the server. It
        should only be set by the client when creating a new user or updating a
        user's password.
        """
        self.role = role
        self.id = id_

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        d["role"] = self.role.value
        return d

    @staticmethod
    def from_dict(d: dict):
        return User(
            username=d["username"],
            password=d["password"],
            role=User.RoleType(d["role"]),
            id_=d["id"],
        )
