from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFocusEvent, QPaintEvent, QPainter
from PyQt5.QtWidgets import QPlainTextEdit


# TODO: Support regular QTextEdit
class PlaceholderTextEdit(QPlainTextEdit):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder_text = ""

    def paintEvent(self, event: QPaintEvent) -> None:
        """https://stackoverflow.com/a/43882058/8134178

        Similar to the placeholder text for QLineEdit, but the text is centered

        Draw the placeholder text when there is no text entered and the widget
        doesn't have focus.
        """
        super().paintEvent(event)

        if self.placeholder_text \
                and not self.hasFocus() \
                and not self.toPlainText():

            painter = QPainter(self.viewport())

            color = self.palette().text().color()
            color.setAlpha(128)
            painter.setPen(color)

            flags = Qt.AlignCenter | Qt.TextWordWrap
            painter.drawText(self.viewport().rect(), flags,
                             self.placeholder_text)

    def focusInEvent(self, event: QFocusEvent) -> None:
        super().focusInEvent(event)

        # https://forum.qt.io/post/381991
        # Redraw the viewport. If this is not here the text will not disappear
        self.viewport().update()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        super().focusOutEvent(event)

        # https://forum.qt.io/post/381991
        # Redraw the viewport. If this is not here the text will not reappear
        self.viewport().update()
