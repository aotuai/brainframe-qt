import datetime
import typing
from typing import Any, Dict

import pendulum
from PyQt5.QtWidgets import QGridLayout, QLabel, QWidget

from brainframe.api import bf_codecs
from .license_terms_ui import _LicenseTermsUI


class LicenseTerms(_LicenseTermsUI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

    def set_license_terms(self, license_terms: bf_codecs.LicenseTerms):
        # TODO: We might want a system in the future that makes this more
        #       versatile
        self._reset()

        license_end = license_terms.expiration_date
        license_end_str = self._license_end_to_str(license_end)

        journal_age = license_terms.journal_max_allowed_age
        journal_age_str = self._journal_age_to_str(journal_age)

        online_checkin_str = "❌" if license_terms.online_checkin else "✔️"

        license_terms = {
            self.tr("License active until"): license_end_str,
            self.tr("Online check-in required"): online_checkin_str,
            self.tr("Max streams"): license_terms.max_streams,
            self.tr("Max journaling age"): journal_age_str
        }
        self._add_license_terms(license_terms)

    def _add_license_terms(self, license_terms: Dict[str, Any]) -> None:

        for row, (term, value) in enumerate(license_terms.items()):
            self.add_term_value(term, str(value), row)

    def add_term_value(self, term: Any, value: Any, row):
        term_label = self._init_value(term)
        value_label = self._init_value(value)

        layout = typing.cast(QGridLayout, self.layout())
        layout.addWidget(term_label, row, 0)
        layout.addWidget(value_label, row, 1)

    def _init_term(self, text) -> QLabel:
        term = QLabel(text, self)

        term.setObjectName("term")

        return term

    def _init_value(self, text) -> QLabel:
        term = QLabel(text, self)

        term.setObjectName("value")

        return term

    def _reset(self) -> None:
        for i in reversed(range(self.layout().count())):
            widget = self.layout().itemAt(i).widget()
            widget.deleteLater()

        # https://stackoverflow.com/a/10439207/8134178
        QWidget().setLayout(self.layout())
        self._init_layout()
        # Refreshes layout style
        self._init_style()

    def _journal_age_to_str(self, journaling_age: float) -> str:
        duration = pendulum.Duration(seconds=journaling_age)

        duration_format = self.tr("{days}d{hours}h{minutes}m")
        duration_str = duration_format.format(
            days=duration.days,
            hours=duration.hours,
            minutes=duration.minutes
        )

        return duration_str

    def _license_end_to_str(
            self, license_end: typing.Optional[datetime.date]) \
            -> str:
        if license_end is None:
            license_period = self.tr("Perpetual License")
        else:
            license_end = self._date_to_pdl_datetime(license_end)
            license_end = license_end.in_timezone('local')
            # TODO: Add localization support. Pendulum's LLL format doesn't
            #           support timezones, unfortunately.
            license_period = license_end.format("MMMM DD, YYYY [at] HH:mm zz")

        return license_period

    # TODO: Don't duplicate code
    @staticmethod
    def _date_to_pdl_datetime(date: datetime.date) -> pendulum.DateTime:
        pdl_datetime = pendulum.datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            tz="UTC")

        return pdl_datetime
