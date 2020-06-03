from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget


class _LicenseDetailsUI(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QVBoxLayout()

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)
