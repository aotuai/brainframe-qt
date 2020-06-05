from typing import Optional

import pendulum
from PyQt5.QtWidgets import QWidget

from brainframe.client.ui.resources.ui_elements.widgets import \
    AspectRatioSVGWidget
from .product_widget_ui import _ProductWidgetUI


class ProductWidget(_ProductWidgetUI):
    def __init__(self, product_name: str, icon_path: str,
                 license_end: Optional[pendulum.DateTime], parent: QWidget):
        super().__init__(parent)

        self.set_product_name(product_name)
        self.set_icon(icon_path)
        self.set_license_end(license_end)

    def set_icon(self, icon_path: str) -> None:
        new_icon = self._init_product_icon(icon_path)
        self.layout().replaceWidget(self.product_icon, new_icon)

        self.product_icon = new_icon

    def set_product_name(self, name: str) -> None:
        self.product_name.setText(name)

    def set_license_end(self, license_end: pendulum.DateTime) -> None:

        if license_end is None:
            license_period = "Perpetual License"
        else:
            date_str = license_end.format("MMMM DD, YYYY")
            license_period = f"License active until {date_str}"

        self.license_period.setText(license_period)
