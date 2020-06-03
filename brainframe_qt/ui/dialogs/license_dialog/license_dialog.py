from PyQt5.QtWidgets import QWidget

from .license_dialog_ui import _LicenseDialogUI


class LicenseDialog(_LicenseDialogUI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_signals()

    def _init_signals(self) -> None:
        ...
