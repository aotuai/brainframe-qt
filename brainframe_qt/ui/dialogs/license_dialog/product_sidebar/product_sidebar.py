from PyQt5.QtWidgets import QWidget

from .product_sidebar_ui import _ProductSidebarUI


class ProductSidebar(_ProductSidebarUI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_signals()

    def _init_signals(self) -> None:
        ...
