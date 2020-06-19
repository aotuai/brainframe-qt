from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from .text_license_editor_ui import _TextLicenseEditorUI


class TextLicenseEditor(_TextLicenseEditorUI):
    license_text_update = pyqtSignal(str)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_signals()

    def _init_signals(self) -> None:
        self.license_textbox.textChanged.connect(self._handle_text_change)
        self.update_license_button.clicked.connect(
            self.publish_license_text_update)

    def publish_license_text_update(self):
        license_key = self.license_textbox.toPlainText()
        self.license_text_update.emit(license_key)

        self.license_textbox.clear()

    def _handle_text_change(self):
        text = self.license_textbox.toPlainText()
        self.update_license_button.setDisabled(text == "" or text.isspace())
