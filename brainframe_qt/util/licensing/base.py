from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

import pendulum
from brainframe.api import bf_codecs


@dataclass
class LicenseInfo:
    state: "LicenseState"
    expiration_date: Optional[pendulum.DateTime]
    terms: bf_codecs.LicenseTerms  # TODO: Convert to core-specific object

    @classmethod
    def from_api_info(cls, license_info: bf_codecs.LicenseInfo) -> "LicenseInfo":
        return cls(
            state=LicenseState.from_api_state(license_info.state),
            expiration_date=license_info.terms.expiration_date,
            terms=license_info.terms,
        )


class LicenseState(Enum):
    VALID = auto()
    """License valid; features should be enabled"""
    INVALID = auto()
    """License exists but is invalid"""
    EXPIRED = auto()
    """License exists but is expired"""
    MISSING = auto()
    """License missing"""

    @classmethod
    def from_api_state(cls, api_state: bf_codecs.LicenseInfo.State) -> "LicenseState":
        state_map = {
            bf_codecs.LicenseInfo.State.VALID: cls.VALID,
            bf_codecs.LicenseInfo.State.INVALID: cls.INVALID,
            bf_codecs.LicenseInfo.State.EXPIRED: cls.EXPIRED,
            bf_codecs.LicenseInfo.State.MISSING: cls.MISSING,
        }
        return state_map[api_state]
