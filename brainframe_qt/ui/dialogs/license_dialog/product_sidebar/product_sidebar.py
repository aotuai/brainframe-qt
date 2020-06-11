from typing import Optional

import pendulum
from PyQt5.QtWidgets import QListWidgetItem, QWidget

from brainframe.api import bf_codecs
from .product_sidebar_ui import _ProductSidebarUI
from .product_widget import ProductWidget


class ProductSidebar(_ProductSidebarUI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_signals()

    def _init_signals(self) -> None:
        ...

    def add_product(self, product_name: str, icon_path: str,
                    license_info: bf_codecs.LicenseInfo) \
            -> None:
        # Create item for widget and add to list
        list_item = QListWidgetItem(self)

        # Create widget
        product = ProductWidget(product_name, icon_path, license_info, self)

        # This is necessary for some reason
        list_item.setSizeHint(product.sizeHint())

        self.addItem(list_item)
        self.setItemWidget(list_item, product)
