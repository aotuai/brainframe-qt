from PyQt5.QtCore import Qt, QObject
from PyQt5.QtWidgets import QDialog, QHBoxLayout

from brainframe_qt.ui.resources import stylesheet_watcher
from brainframe_qt.ui.resources.paths import qt_qss_paths
from .widgets import ProductSidebar
from .widgets.brainframe_license import LicenseDetails


class _LicenseDialogUI(QDialog):
    def __init__(self, *, parent: QObject):
        super().__init__(parent=parent)

        self.product_sidebar = self._init_product_sidebar()
        self.license_details = self._init_license_details()

        self._init_layout()
        self._init_style()

    def _init_product_sidebar(self) -> ProductSidebar:
        product_sidebar = ProductSidebar(parent=self)

        return product_sidebar

    def _init_license_details(self) -> LicenseDetails:
        license_details = LicenseDetails(parent=self)

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

        self.layout().setContentsMargins(0, 0, 0, 0)
