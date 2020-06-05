from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget, QWidget


class _ProductSidebarUI(QListWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_style()

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)
