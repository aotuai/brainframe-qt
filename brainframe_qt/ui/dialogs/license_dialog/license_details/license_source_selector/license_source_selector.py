from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QTextOption
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QStackedWidget, QTextEdit, \
    QVBoxLayout, QWidget

from .license_source_buttons import LicenseSourceButtons


class LicenseSourceSelector(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.license_source_label = self._init_license_source_label()
        self.license_source_buttons = self._init_license_source_buttons()

        self.license_textbox = self._init_license_textbox()
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

    def _init_license_textbox(self) -> QTextEdit:
        license_textbox = QTextEdit(self)

        return license_textbox

    def _init_license_stack_widget(self) -> QStackedWidget:
        license_stack_widget = QStackedWidget(self)

        license_stack_widget.addWidget(self.license_textbox)

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

        # TODO: Verify that this works on all builds
        # https://stackoverflow.com/q/1468022/8134178
        monospace_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.license_textbox.setFont(monospace_font)

        self.license_textbox.setWordWrapMode(QTextOption.WrapAnywhere)
