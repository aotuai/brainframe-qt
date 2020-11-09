from typing import Callable

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QWidget


class OverlayTitlebar(QFrame):
    label: Callable[..., QHBoxLayout]

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)

        self.title_label = self._init_title_label()

        self._init_layout()
        self._init_style()

    def _init_title_label(self) -> QLabel:
        title_label = QLabel("[Stream Name]", self)

        return title_label

    def _init_layout(self) -> None:
        layout = QHBoxLayout()

        layout.addWidget(self.title_label)

        self.setLayout(layout)

    def _init_style(self) -> None:
        self.layout().setAlignment(Qt.AlignLeft)

        self.title_label.setSizePolicy(QSizePolicy.Maximum,
                                       QSizePolicy.Preferred)
