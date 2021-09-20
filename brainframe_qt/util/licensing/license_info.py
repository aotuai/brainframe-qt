from dataclasses import dataclass
from enum import Enum, auto
from brainframe.api import bf_codecs


@dataclass
class LicensedProduct:
    name: str
    icon_resource: str  # Qt resource path, not file path
    license_info: bf_codecs.LicenseInfo  # TODO: Make domain-specific


# @dataclass
# class LicenseInfo:
#     state: "LicenseState"
#     expiration_date: Optional[pendulum.DateTime]
#     terms: dict


class LicenseState(Enum):
    VALID = auto()
    """License valid; features should be enabled"""
    INVALID = auto()
    """License exists but is invalid"""
    EXPIRED = auto()
    """License exists but is expired"""
    MISSING = auto()
    """License missing"""
