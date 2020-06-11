import datetime

import pendulum
from PyQt5.QtWidgets import QWidget

from brainframe.api import bf_codecs
from .license_details_ui import _LicenseDetailsUI


class LicenseDetails(_LicenseDetailsUI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_signals()

    def _init_signals(self) -> None:
        ...

    def set_product(self, product_name, license_info: bf_codecs.LicenseInfo) \
            -> None:
        self.set_product_name(product_name)
        # self.set_licensee(license_info.licensee)

        license_end = license_info.terms.expiration_date
        if license_end is not None:
            license_end = self._date_to_pdl_datetime(license_end)
        self.set_license_end(license_end)

    def set_product_name(self, product_name: str) -> None:
        self.product_name.setText(product_name)

    def set_licensee(self, licensee: str) -> None:
        self.licensee.setText(licensee)

    def set_license_end(self, license_end: pendulum.DateTime) -> None:

        if license_end is None:
            license_period = "Perpetual License"
        else:
            license_period = license_end.format(self.LICENSE_END_FORMAT)

        self.license_end.setText(license_period)

    # TODO: Don't duplicate code
    @staticmethod
    def _date_to_pdl_datetime(date: datetime.date) -> pendulum.DateTime:
        pdl_datetime = pendulum.datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            tz="UTC")

        return pdl_datetime
