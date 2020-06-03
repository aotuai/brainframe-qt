from PyQt5.QtWidgets import QWidget

from .license_details_ui import _LicenseDetailsUI


class LicenseDetails(_LicenseDetailsUI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_signals()

    def _init_signals(self) -> None:
        ...
