import pendulum
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QLabel, QWidget

from .license_source_selector import LicenseSourceSelector


class _LicenseDetailsUI(QWidget):

    LICENSE_END_FORMAT = "MMMM DD, YYYY [at] HH:mm:ss zz"

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.product_name = self._init_product_name()

        self.licensee_label = self._init_licensee_label()
        self.licensee = self._init_licensee()

        self.license_end_label = self._init_license_end_label()
        self.license_end = self._init_license_end()

        self.license_source_selector = self._init_license_source_selector()

        self._init_layout()
        self._init_style()

    def _init_product_name(self) -> QLabel:
        label_text = "[Product Name]"
        product_name = QLabel(label_text, self)

        return product_name

    def _init_licensee_label(self) -> QLabel:
        label_text = self.tr("Licensed to:")
        licensee_label = QLabel(label_text, self)

        return licensee_label

    def _init_licensee(self) -> QLabel:
        licensee = QLabel("[Licensee]", self)

        return licensee

    def _init_license_end_label(self) -> QLabel:
        label_text = self.tr("License active until:")
        license_end_label = QLabel(label_text, self)

        return license_end_label

    def _init_license_end(self) -> QLabel:
        # Epoch time as a default
        default_end_time = pendulum.datetime(1970, 1, 1)
        license_end_str = default_end_time.format(self.LICENSE_END_FORMAT)

        license_end = QLabel(license_end_str, self)

        return license_end

    def _init_license_source_selector(self) -> LicenseSourceSelector:
        license_source_selector = LicenseSourceSelector(self)

        return license_source_selector

    def _init_layout(self) -> None:
        layout = QGridLayout()

        layout.addWidget(self.product_name, 0, 0, 1, 2)

        layout.addWidget(self.licensee_label, 1, 0)
        layout.addWidget(self.licensee, 1, 1)
        layout.addWidget(self.license_end_label, 2, 0)
        layout.addWidget(self.license_end, 2, 1)
        layout.addWidget(self.license_source_selector, 3, 0, 1, 2)

        # TODO: These are hidden because the information is not provided by
        #       the server yet
        self.licensee_label.hide()
        self.licensee.hide()

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.layout().setAlignment(Qt.AlignTop)
