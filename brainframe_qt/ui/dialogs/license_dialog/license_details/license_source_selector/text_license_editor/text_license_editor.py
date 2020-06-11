from PyQt5.QtWidgets import QWidget

from .text_license_editor_ui import _TextLicenseEditorUI


class TextLicenseEditor(_TextLicenseEditorUI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_signals()

    def _init_signals(self) -> None:
        ...
