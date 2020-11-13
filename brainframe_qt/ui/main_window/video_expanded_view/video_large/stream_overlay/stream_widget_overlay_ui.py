from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from .body import OverlayBody
from .titlebar import OverlayTitlebar


class StreamWidgetOverlayUI(QWidget):
    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)

        self.titlebar = self._init_titlebar()
        self.body = self._init_body()

        self._init_layout()
        self._init_style()

    def _init_titlebar(self) -> OverlayTitlebar:
        titlebar = OverlayTitlebar(parent=self)

        return titlebar

    def _init_body(self) -> OverlayBody:
        body = OverlayBody(parent=self)

        return body

    def _init_layout(self) -> None:
        layout = QVBoxLayout()

        layout.addWidget(self.titlebar)
        layout.addWidget(self.body)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.layout().setContentsMargins(0, 0, 0, 0)
