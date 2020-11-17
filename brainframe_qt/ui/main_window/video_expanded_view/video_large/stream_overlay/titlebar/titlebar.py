from typing import Callable, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, \
    QSizePolicy, QWidget


class OverlayTitlebar(QFrame):
    label: Callable[..., QHBoxLayout]

    NO_STREAM_NAME = QApplication.translate("OverlayTitlebar",
                                            "No Active Stream")

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

    def set_stream_name(self, stream_name: Optional[str]) -> None:
        if stream_name is None:
            self.title_label.setText(self.NO_STREAM_NAME)
        else:
            self.title_label.setText(stream_name)
