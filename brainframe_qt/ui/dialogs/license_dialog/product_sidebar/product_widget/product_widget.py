import typing
from datetime import datetime

import pendulum
from PyQt5.QtWidgets import QWidget

from brainframe.api import bf_codecs
from .product_widget_ui import _ProductWidgetUI


class ProductWidget(_ProductWidgetUI):
    def __init__(self, product_name: str, icon_path: str,
                 license_info: bf_codecs.LicenseInfo, parent: QWidget):
        super().__init__(parent)

        self.set_icon(icon_path)

        self._product_name = typing.cast(str, None)
        self.product_name = product_name

        self._license_info = typing.cast(bf_codecs.LicenseInfo, None)
        self.license_info = license_info

    @property
    def license_info(self) -> bf_codecs.LicenseInfo:
        return self._license_info

    @license_info.setter
    def license_info(self, license_info: bf_codecs.LicenseInfo):
        self._license_info = license_info

        # Convert date to a pendulum UTC datetime
        expiration_date = license_info.terms.expiration_date
        if expiration_date is not None:
            expiration_date = self._date_to_pdl_datetime(expiration_date)

        self.set_license_end(expiration_date)

    def set_icon(self, icon_path: str) -> None:
        new_icon = self._init_product_icon(icon_path)
        self.layout().replaceWidget(self.product_icon, new_icon)

        self.product_icon.deleteLater()
        self.product_icon = new_icon

    @property
    def product_name(self) -> str:
        return self._product_name

    @product_name.setter
    def product_name(self, product_name: str) -> None:
        self._product_name = product_name
        self.product_name_label.setText(product_name)

    def set_license_end(self, license_end: pendulum.DateTime) -> None:

        if license_end is None:
            license_period = "Perpetual License"
        else:
            date_str = license_end.format("MMMM DD, YYYY")
            license_period = f"License active until {date_str}"

        self.license_period.setText(license_period)

    @staticmethod
    def _date_to_pdl_datetime(date: datetime.date) -> pendulum.DateTime:
        pdl_datetime = pendulum.datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            tz="UTC")

        return pdl_datetime
