from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from brainframe.client.ui.resources.ui_elements.widgets import \
    AspectRatioSVGWidget


class _ProductWidgetUI(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.product_icon = self._init_product_icon()
        self.product_name = self._init_product_name()
        self.license_period = self._init_license_period()

        self._init_layout()
        self._init_style()

    def _init_product_icon(self, icon_path: Optional[str] = None) \
            -> AspectRatioSVGWidget:
        if icon_path is None:
            # TODO: Use a different icon
            icon_path = ":/icons/capsule_toolbar"
        product_icon = AspectRatioSVGWidget(icon_path, self)

        product_icon.setObjectName("product_icon")

        return product_icon

    def _init_product_name(self) -> QLabel:
        product_title = QLabel("[Product Name]", self)

        return product_title

    def _init_license_period(self) -> QLabel:
        license_period = QLabel("[License Period]", self)

        return license_period

    def _init_layout(self) -> None:
        main_layout = QHBoxLayout()
        text_layout = QVBoxLayout()

        main_layout.addWidget(self.product_icon)
        main_layout.addLayout(text_layout)

        text_layout.addWidget(self.product_name)
        text_layout.addWidget(self.license_period)

        self.setLayout(main_layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)
