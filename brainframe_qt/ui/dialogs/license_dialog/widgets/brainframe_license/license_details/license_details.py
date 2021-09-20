from PyQt5.QtCore import pyqtSignal, QObject

from brainframe_qt.util.licensing.license_info import LicensedProduct, LicenseState
from .license_details_ui import _LicenseDetailsUI


class LicenseDetails(_LicenseDetailsUI):
    license_text_update = pyqtSignal(str)
    oauth_login_requested = pyqtSignal()

    def __init__(self, *, parent: QObject):
        super().__init__(parent=parent)

        self._init_signals()

    def _init_signals(self) -> None:
        self.license_source_selector.license_text_update.connect(
            self.license_text_update)
        self.license_source_selector.oauth_login_requested.connect(
            self.oauth_login_requested)

    def set_product(self, product: LicensedProduct) -> None:
        self.product_name = product.name

        if product.license_info.state is LicenseState.MISSING:
            self.license_terms.hide()
            self.missing_license_message.show()
        elif product.license_info.state is LicenseState.INVALID:
            self.license_terms.hide()
            self.invalid_license_message.show()
        elif product.license_info.state is LicenseState.EXPIRED:
            # TODO: BF-1328
            self.license_terms.hide()
            self.expired_license_message.show()
        else:
            self.license_terms.show()
            self.missing_license_message.hide()
            self.invalid_license_message.hide()
            self.expired_license_message.hide()
            self.license_terms.set_license_terms(product.license_info.terms)

    @property
    def product_name(self) -> str:
        return self.product_name_label.text()

    @product_name.setter
    def product_name(self, product_name: str) -> None:
        self.product_name_label.setText(product_name)

    def set_licensee(self, licensee: str) -> None:
        self.licensee.setText(licensee)
