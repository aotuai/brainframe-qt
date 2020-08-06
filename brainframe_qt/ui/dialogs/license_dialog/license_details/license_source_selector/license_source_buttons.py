from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QButtonGroup, QHBoxLayout, QRadioButton, \
    QWidget


class LicenseSourceButtons(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.license_key_button = self._init_license_key_button()
        self.aotu_account_button = self._init_aotu_account_button()

        self.button_group = self._init_button_group()

        self._init_layout()
        self._init_style()

    def _init_license_key_button(self) -> QRadioButton:
        button_text = self.tr("License Key")
        license_key_button = QRadioButton(button_text, self)

        return license_key_button

    def _init_aotu_account_button(self) -> QRadioButton:
        button_text = self.tr("Aotu Account")
        aotu_account_button = QRadioButton(button_text, self)

        aotu_account_button.setDisabled(True)
        tooltip_text = self.tr("Coming soon")
        aotu_account_button.setToolTip(tooltip_text)

        return aotu_account_button

    def _init_button_group(self) -> QButtonGroup:
        button_group = QButtonGroup(self)

        button_group.addButton(self.license_key_button)
        button_group.addButton(self.aotu_account_button)

        button_group.setExclusive(True)
        self.license_key_button.setChecked(True)

        return button_group

    def _init_layout(self) -> None:
        layout = QHBoxLayout(self)

        layout.addWidget(self.license_key_button)
        layout.addWidget(self.aotu_account_button)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.layout().setContentsMargins(0, 0, 0, 0)
