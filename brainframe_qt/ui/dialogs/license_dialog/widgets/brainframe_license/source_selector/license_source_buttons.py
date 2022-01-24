from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QButtonGroup, QHBoxLayout, QRadioButton, \
    QWidget, QAbstractButton

from brainframe_qt.util.licensing import LicenseManager


class LicenseSourceButtons(QWidget):
    license_source_changed = pyqtSignal(str)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.license_key_button = self._init_license_key_button()
        self.aotu_account_button = self._init_aotu_account_button()

        self.button_group = self._init_button_group()

        self._init_layout()
        self._init_style()

        self._init_signals()

    def _init_aotu_account_button(self) -> QRadioButton:
        button_text = self.tr("Aotu Account")
        aotu_account_button = QRadioButton(button_text, self)

        if not LicenseManager.is_oauth_available():
            aotu_account_button.setDisabled(True)

        return aotu_account_button

    def _init_license_key_button(self) -> QRadioButton:
        button_text = self.tr("License Key")
        license_key_button = QRadioButton(button_text, self)

        return license_key_button

    def _init_button_group(self) -> QButtonGroup:
        button_group = QButtonGroup(self)

        button_group.addButton(self.aotu_account_button)
        button_group.addButton(self.license_key_button)

        button_group.setExclusive(True)
        self.aotu_account_button.setChecked(True)

        return button_group

    def _init_layout(self) -> None:
        layout = QHBoxLayout(self)

        layout.addWidget(self.aotu_account_button)
        layout.addWidget(self.license_key_button)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.layout().setContentsMargins(0, 0, 0, 0)

    def _init_signals(self) -> None:
        self.button_group.buttonClicked.connect(
            self._handle_license_button_change
        )

    def _handle_license_button_change(self, button: QAbstractButton) -> None:
        if button is self.license_key_button:
            license_source = "license_file"
        elif button is self.aotu_account_button:
            license_source = "aotu_account"
        else:
            raise ValueError("Unknown license source button")

        self.license_source_changed.emit(license_source)
