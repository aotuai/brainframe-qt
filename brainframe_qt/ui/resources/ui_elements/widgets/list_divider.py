from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from brainframe_qt.ui.resources.ui_elements.widgets import Line


class ListDivider(QWidget):

    def __init__(self, text: str, parent: QWidget):
        super().__init__(parent)

        self.left_line = Line(QFrame.HLine, self)
        self.text_label = QLabel(text, self)
        self.right_line = Line(QFrame.HLine, self)

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QHBoxLayout()

        layout.addWidget(self.left_line)
        layout.addWidget(self.text_label)
        layout.addWidget(self.right_line)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)
