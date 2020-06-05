from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QWidget

from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.paths import qt_qss_paths
from .product_sidebar import ProductSidebar
from .license_details import LicenseDetails


class _LicenseDialogUI(QDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.product_sidebar = self._init_product_sidebar()
        self.license_details = self._init_license_details()

        self._init_layout()
        self._init_style()

    def _init_product_sidebar(self) -> ProductSidebar:
        product_sidebar = ProductSidebar(self)

        return product_sidebar

    def _init_license_details(self) -> LicenseDetails:
        license_details = LicenseDetails(self)

        return license_details

    def _init_layout(self) -> None:
        layout = QHBoxLayout()

        layout.addWidget(self.product_sidebar)
        layout.addWidget(self.license_details)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.license_dialog_qss)
