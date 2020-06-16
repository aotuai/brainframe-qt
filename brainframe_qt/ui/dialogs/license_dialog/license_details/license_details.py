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

        self.license_terms.set_license_terms(license_info.terms)

    def set_product_name(self, product_name: str) -> None:
        self.product_name.setText(product_name)

    def set_licensee(self, licensee: str) -> None:
        self.licensee.setText(licensee)
