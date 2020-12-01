from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFrame, QGridLayout, QLabel, QWidget

from brainframe_qt.ui.resources.links.documentation import \
    LICENSE_DOCS_LINK
from brainframe_qt.ui.resources.ui_elements.widgets import Line
from .license_source_selector import LicenseSourceSelector
from .license_terms import LicenseTerms


class _LicenseDetailsUI(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.product_name_label = self._init_product_name_label()

        self.license_terms = self._init_license_terms()
        self.missing_license_message = self._init_missing_license_message()
        self.invalid_license_message = self._init_invalid_license_message()
        self.expired_license_message = self._init_expired_license_message()

        self.licensee_label = self._init_licensee_label()
        self.licensee = self._init_licensee()

        self.license_source_selector = self._init_license_source_selector()

        self._init_layout()
        self._init_style()

    def _init_product_name_label(self) -> QLabel:
        label_text = "[Product Name]"
        product_name_label = QLabel(label_text, self)

        product_name_label.setObjectName("product_name")

        return product_name_label

    def _init_missing_license_message(self) -> QLabel:
        message_text = QApplication.translate(
            "LicenseDetails",
            "No license exists on the server. Please "
            "<a href='{license_docs_link}'>upload one</a>."
        ).format(license_docs_link=LICENSE_DOCS_LINK)

        missing_license_message = QLabel(message_text, self)

        missing_license_message.setObjectName("error_message")
        missing_license_message.setOpenExternalLinks(True)

        return missing_license_message

    def _init_invalid_license_message(self) -> QLabel:
        message_text = QApplication.translate(
            "LicenseDetails",
            "Server holds an invalid license or the BrainFrame server was "
            "unable to talk to Aotu's licensing servers.<br>"
            "Please <a href='{license_docs_link}'>upload a new license</a> or "
            "ensure that the server is connected to the internet."
        ).format(license_docs_link=LICENSE_DOCS_LINK)

        invalid_license_message = QLabel(message_text, self)

        invalid_license_message.setObjectName("error_message")
        invalid_license_message.setOpenExternalLinks(True)

        return invalid_license_message

    def _init_expired_license_message(self) -> QLabel:
        message_text = QApplication.translate(
            "LicenseDetails",
            "License is expired. Please "
            "<a href='{license_docs_link}'>upload a new one</a>."
        ).format(license_docs_link=LICENSE_DOCS_LINK)

        expired_license_message = QLabel(message_text, self)

        expired_license_message.setObjectName("error_message")
        expired_license_message.setOpenExternalLinks(True)

        return expired_license_message

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

        layout.addWidget(self.product_name_label, 0, 0, 1, 2)

        layout.addWidget(Line(QFrame.HLine, self), 1, 0, 1, 2)

        layout.addWidget(self.licensee_label, 2, 0)
        layout.addWidget(self.licensee, 2, 1)

        layout.addWidget(self.missing_license_message, 3, 0, 1, 2)
        layout.addWidget(self.invalid_license_message, 4, 0, 1, 2)
        layout.addWidget(self.expired_license_message, 5, 0, 1, 2)

        layout.addWidget(self.license_terms, 6, 0, 1, 2)
        layout.addWidget(self.license_source_selector, 7, 0, 1, 2)

        # TODO: These are hidden because the information is not provided by
        #       the server yet
        self.licensee_label.hide()
        self.licensee.hide()

        # Hide error messages
        self.missing_license_message.hide()
        self.invalid_license_message.hide()
        self.expired_license_message.hide()

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.layout().setAlignment(Qt.AlignTop)
