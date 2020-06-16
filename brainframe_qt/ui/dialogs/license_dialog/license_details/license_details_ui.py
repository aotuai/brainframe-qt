from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QGridLayout, QLabel, QWidget

from brainframe.client.ui.resources.ui_elements.widgets import Line
from .license_source_selector import LicenseSourceSelector
from .license_terms import LicenseTerms


class _LicenseDetailsUI(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.product_name = self._init_product_name()

        self.licensee_label = self._init_licensee_label()
        self.licensee = self._init_licensee()

        self.license_source_selector = self._init_license_source_selector()

        self.license_terms = self._init_license_terms()

        self._init_layout()
        self._init_style()

    def _init_product_name(self) -> QLabel:
        label_text = "[Product Name]"
        product_name = QLabel(label_text, self)

        product_name.setObjectName("product_name")

        return product_name

    def _init_licensee_label(self) -> QLabel:
        label_text = self.tr("Licensed to:")
        licensee_label = QLabel(label_text, self)

        return licensee_label

    def _init_licensee(self) -> QLabel:
        licensee = QLabel("[Licensee]", self)

        return licensee

    def _init_license_source_selector(self) -> LicenseSourceSelector:
        license_source_selector = LicenseSourceSelector(self)

        return license_source_selector

    def _init_license_terms(self) -> LicenseTerms:
        license_terms = LicenseTerms(self)

        return license_terms

    def _init_layout(self) -> None:
        layout = QGridLayout()

        layout.addWidget(self.product_name, 0, 0, 1, 2)

        layout.addWidget(Line(QFrame.HLine, self), 1, 0, 1, 2)

        layout.addWidget(self.licensee_label, 2, 0)
        layout.addWidget(self.licensee, 2, 1)
        layout.addWidget(self.license_terms, 3, 0, 1, 2)
        layout.addWidget(self.license_source_selector, 4, 0, 1, 2)

        # TODO: These are hidden because the information is not provided by
        #       the server yet
        self.licensee_label.hide()
        self.licensee.hide()

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.layout().setAlignment(Qt.AlignTop)

        # Remove contents margins from top and bottom
        contents_margins = self.layout().contentsMargins()
        contents_margins.setBottom(0)
        contents_margins.setTop(0)
        self.layout().setContentsMargins(contents_margins)