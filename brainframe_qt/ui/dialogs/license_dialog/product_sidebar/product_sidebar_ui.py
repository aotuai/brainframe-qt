import pendulum
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QWidget

from .product_widget import ProductWidget


class _ProductSidebarUI(QListWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_style()

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

    def add_product(self, product_name: str, icon_path: str,
                    expiration_datetime: pendulum.DateTime) -> None:
        # Create widget
        product = ProductWidget(
            product_name, icon_path, expiration_datetime, self)

        # Create item for widget and add to list
        list_item = QListWidgetItem(self)
        self.setItemWidget(list_item, product)
        self.addItem(list_item)
