from typing import Callable

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget


class OverlayBody(QWidget):
    layout: Callable[..., QHBoxLayout]

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)

        self.button_widget = self._init_button_widget()
        self.tray = self._init_tray()

        self._init_layout()
        self._init_style()

    def _init_tray(self) -> ...:
        return QWidget(parent=self)

    def _init_button_widget(self) -> ...:
        return QWidget(parent=self)

    def _init_layout(self) -> None:
        main_layout = QHBoxLayout()
        content_layout = QVBoxLayout()

        main_layout.addLayout(content_layout)
        main_layout.addWidget(self.button_widget)

        content_layout.addStretch()
        content_layout.addWidget(self.tray)

        self.setLayout(main_layout)

    def _init_style(self) -> None:
        ...
