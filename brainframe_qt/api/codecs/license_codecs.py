from datetime import date, datetime
from typing import Optional

from brainframe.shared import codec_enums
from brainframe.client.api.codecs.base_codecs import Codec


class LicenseTerms(Codec):
    """The terms of the currently active license."""

    def __init__(self, *,
                 online_checkin: bool,
                 max_streams: int,
                 journal_max_allowed_age: float,
                 expiration_date: Optional[date]):
        self.online_checkin = online_checkin
        self.max_streams = max_streams
        self.journal_max_allowed_age = journal_max_allowed_age
        self.expiration_date = expiration_date

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        if self.expiration_date is not None:
            d["expiration_date"] = self.expiration_date.strftime(DATE_FORMAT)
        return d

    @staticmethod
    def from_dict(d: dict) -> "LicenseTerms":
        expiration_date = None
        if d["expiration_date"] is not None:
            expiration_date = datetime.strptime(
                d["expiration_date"], DATE_FORMAT).date()

        terms = LicenseTerms(
            online_checkin=d["online_checkin"],
            max_streams=d["max_streams"],
            journal_max_allowed_age=d["journal_max_allowed_age"],
            expiration_date=expiration_date,
        )
        return terms


class LicenseInfo(Codec):
    """Information on the licensing status of the server"""

    State = codec_enums.LicenseState

    def __init__(self, *, state: State, terms: Optional[LicenseTerms]):
        self.state = state
        self.terms = terms

    def to_dict(self) -> dict:
        return {
            "state": self.state.value,
            "terms": self.terms.to_dict() if self.terms else None,
        }

    @staticmethod
    def from_dict(d: dict) -> "LicenseInfo":
        terms = None
        if d["terms"] is not None:
            terms = LicenseTerms.from_dict(d["terms"])

        return LicenseInfo(
            state=LicenseInfo.State(d["state"]),
            terms=terms,
        )


DATE_FORMAT = "%Y-%m-%d"
"""ISO 8601 date format used by the API"""
