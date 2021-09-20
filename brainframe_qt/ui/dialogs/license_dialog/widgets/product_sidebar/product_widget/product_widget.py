import typing
from typing import Optional

import pendulum
from PyQt5.QtWidgets import QWidget

from brainframe_qt.util.licensing import LicenseState
from .product_widget_ui import _ProductWidgetUI
from ....core.base import LicensedProduct


class ProductWidget(_ProductWidgetUI):
    def __init__(self, product: LicensedProduct, *, parent: QWidget):
        super().__init__(parent=parent)

        self.product = typing.cast(LicensedProduct, None)
        self.set_product(product)

    def set_product(self, product: LicensedProduct) -> None:
        self.product = product

        self._set_icon(product.icon_resource)
        self._set_product_name(product.name)

        expiration_date: Optional[pendulum.DateTime]
        if product.license_info.state is LicenseState.VALID:
            expiration_date = product.license_info.expiration_date
        else:
            expiration_date = None

        self._set_license_end(expiration_date, product.license_info.state)

    def _set_icon(self, icon_resource: str) -> None:
        new_icon = self._init_product_icon(icon_resource)
        self.layout().replaceWidget(self.product_icon, new_icon)

        self.product_icon.deleteLater()
        self.product_icon = new_icon

    def _set_product_name(self, product_name: str) -> None:
        self._product_name = product_name
        self.product_name_label.setText(product_name)

    def _set_license_end(self, license_end: typing.Optional[pendulum.DateTime],
                        license_state: LicenseState) \
            -> None:

        if license_state is LicenseState.MISSING:
            license_period = self.tr("Unlicensed")
        elif license_state is LicenseState.INVALID:
            license_period = self.tr("Invalid License")
        elif license_state is LicenseState.EXPIRED:
            license_period = self.tr("Expired License")
        else:
            if license_end is None:
                license_period = self.tr("Perpetual License")
            else:
                license_end = license_end.in_timezone('local')
                date_str = license_end.format("MMM DD, YYYY")
                license_period = self.tr("Active until {date_str}") \
                    .format(date_str=date_str)

        self.license_period.setText(license_period)
