import typing
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QMessageBox, QSizePolicy, QSpacerItem, \
    QTextEdit, \
    QWidget


class _BrainFrameMessageUI(QMessageBox):
    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)

        self._init_style()

    def expand_width(self):
        """This needs to be called after doing basically anything...

        QMessageBox sure loves to call .setupLayout()
        """
        # Trick to set the width of the message dialog
        # http://www.qtcentre.org/threads/22298-QMessageBox-Controlling-the-width
        # noinspection PyArgumentList
        spacer = QSpacerItem(600, 0,
                             QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout = typing.cast(QGridLayout, self.layout())
        next_row = layout.rowCount()
        num_cols = layout.columnCount()
        layout.addItem(spacer, next_row, 0, 1, num_cols)

    def expand_traceback_height(self):
        [textbox] = typing.cast(List[QTextEdit], self.findChildren(QTextEdit))
        textbox.setFixedHeight(200)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setTextFormat(Qt.RichText)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.expand_width()
