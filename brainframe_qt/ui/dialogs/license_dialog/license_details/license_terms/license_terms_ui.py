from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QWidget


class _LicenseTermsUI(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QGridLayout()

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.layout().setContentsMargins(0, 0, 0, 0)
