import pendulum
from PyQt5.QtWidgets import QWidget

from brainframe.client.ui.resources.ui_elements.widgets import \
    AspectRatioSVGWidget
from .product_widget_ui import _ProductWidgetUI


class ProductWidget(_ProductWidgetUI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

    def set_icon(self, icon_path: str) -> None:
        new_icon = AspectRatioSVGWidget(icon_path, self)
        self.layout().replaceWidget(self.product_icon, new_icon)

        self.product_icon = new_icon

    def set_product_name(self, name: str):
        self.product_name.setText(name)

    def set_license_end_datetime(self, end_datetime: pendulum.DateTime):
        date_str = end_datetime.format("MMMM DD, YYYY")
        self.license_period = f"License active until {date_str}"
