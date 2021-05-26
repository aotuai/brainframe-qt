import typing

from PyQt5.QtWidgets import QListWidgetItem, QWidget

from ....domain.product import LicensedProduct
from ..product_widget import ProductWidget
from .product_sidebar_ui import _ProductSidebarUI


class ProductSidebar(_ProductSidebarUI):
    def __init__(self, *, parent: QWidget):
        super().__init__(parent)

    def add_product(self, product: LicensedProduct) -> None:
        # Create item for widget and add to list
        list_item = QListWidgetItem(self)

        # Create widget
        product = ProductWidget(product, parent=self)

        # This is necessary for some reason
        list_item.setSizeHint(product.sizeHint())

        self.addItem(list_item)
        self.setItemWidget(list_item, product)

    def update_product(self, product: LicensedProduct) -> None:
        # Find the correct widget
        for row in range(self.count()):
            item = self.item(row)
            widget = typing.cast(ProductWidget, self.itemWidget(item))

            if widget.product.name == product.name:
                widget.set_product(product)
                break
        else:
            # The product is inexplicably missing
            message = f"Unable to update the license information for {product.name}"
            raise LookupError(message)
