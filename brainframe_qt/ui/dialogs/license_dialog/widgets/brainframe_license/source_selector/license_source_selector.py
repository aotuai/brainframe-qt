from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel, QStackedWidget, QVBoxLayout, \
    QWidget

from brainframe_qt.util.licensing import LicenseManager
from ..aotu_login_form import AotuLoginForm
from ..text_license_editor import TextLicenseEditor
from .license_source_buttons import LicenseSourceButtons


class LicenseSourceSelector(QWidget):
    license_text_update = pyqtSignal(str)
    oauth_login_requested = pyqtSignal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.license_source_label = self._init_license_source_label()
        self.license_source_buttons = self._init_license_source_buttons()

        if LicenseManager.is_oauth_available():
            self.aotu_login_form = self._init_aotu_login_form()
        else:
            self.aotu_login_form = None

        self.text_license_editor = self._init_text_license_editor()
        self.license_stack_widget = self._init_license_stack_widget()

        self._source_selector_layout = self._init_source_selector_layout()
        self._init_layout()
        self._init_style()

        self._init_signals()

    def _init_license_source_label(self) -> QLabel:
        label_text = self.tr("Get license from:")
        license_source_label = QLabel(label_text, self)

        return license_source_label

    def _init_license_source_buttons(self) -> LicenseSourceButtons:
        license_source_buttons = LicenseSourceButtons(self)

        return license_source_buttons

    def _init_aotu_login_form(self) -> AotuLoginForm:
        aotu_login_form = AotuLoginForm(parent=self)

        return aotu_login_form

    def _init_text_license_editor(self) -> TextLicenseEditor:
        text_license_editor = TextLicenseEditor(self)

        return text_license_editor

    def _init_license_stack_widget(self) -> QStackedWidget:
        license_stack_widget = QStackedWidget(self)

        if LicenseManager.is_oauth_available():
            license_stack_widget.addWidget(self.aotu_login_form)
        license_stack_widget.addWidget(self.text_license_editor)

        if LicenseManager.is_oauth_available():
            license_stack_widget.setCurrentWidget(self.aotu_login_form)

        return license_stack_widget

    def _init_source_selector_layout(self) -> QVBoxLayout:
        source_selector_layout = QVBoxLayout()

        source_selector_layout.addWidget(self.license_source_label)
        source_selector_layout.addWidget(self.license_source_buttons)

        return source_selector_layout

    def _init_layout(self) -> None:
        main_layout = QVBoxLayout()

        main_layout.addLayout(self._source_selector_layout)
        main_layout.addWidget(self.license_stack_widget)

        self.setLayout(main_layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.layout().setContentsMargins(0, 0, 0, 0)

        self._source_selector_layout.setAlignment(Qt.AlignLeft)

    def _init_signals(self) -> None:
        self.license_source_buttons.license_source_changed.connect(
            self._change_license_source
        )

        self.text_license_editor.license_text_update.connect(
            self.license_text_update)

        if LicenseManager.is_oauth_available():
            self.aotu_login_form.oath_login_requested.connect(
                self.oauth_login_requested)

    def _change_license_source(self, license_source: str) -> None:
        if license_source == "aotu_account":
            if not LicenseManager.is_oauth_available():
                raise RuntimeError("OAuth is not available on this platform.")
            desired_widget = self.aotu_login_form
        elif license_source == "license_file":
            desired_widget = self.text_license_editor
        else:
            raise ValueError(f"Unknown license source {license_source}")

        self.license_stack_widget.setCurrentWidget(desired_widget)
