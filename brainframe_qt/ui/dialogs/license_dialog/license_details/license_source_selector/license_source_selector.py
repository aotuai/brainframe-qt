from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QStackedWidget, QVBoxLayout, \
    QWidget

from .license_source_buttons import LicenseSourceButtons
from .text_license_editor import TextLicenseEditor


class LicenseSourceSelector(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.license_source_label = self._init_license_source_label()
        self.license_source_buttons = self._init_license_source_buttons()

        self.text_license_editor = self._init_text_license_editor()
        self.license_stack_widget = self._init_license_stack_widget()

        self._init_layout()
        self._init_style()

    def _init_license_source_label(self) -> QLabel:
        label_text = self.tr("License Source:")
        license_source_label = QLabel(label_text, self)

        return license_source_label

    def _init_license_source_buttons(self) -> LicenseSourceButtons:
        license_source_buttons = LicenseSourceButtons(self)

        return license_source_buttons

    def _init_text_license_editor(self) -> TextLicenseEditor:
        text_license_editor = TextLicenseEditor(self)

        return text_license_editor

    def _init_license_stack_widget(self) -> QStackedWidget:
        license_stack_widget = QStackedWidget(self)

        license_stack_widget.addWidget(self.text_license_editor)

        return license_stack_widget

    def _init_layout(self) -> None:
        main_layout = QVBoxLayout()

        source_selector_layout = QHBoxLayout()
        source_selector_layout.addWidget(self.license_source_label)
        source_selector_layout.addWidget(self.license_source_buttons)

        main_layout.addLayout(source_selector_layout)
        main_layout.addWidget(self.license_stack_widget)

        self.setLayout(main_layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.layout().setContentsMargins(0, 0, 0, 0)
