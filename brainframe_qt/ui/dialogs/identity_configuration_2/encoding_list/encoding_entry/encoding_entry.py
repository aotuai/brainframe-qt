from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QStyle, \
    QStyleOptionButton
from PyQt5.uic import loadUi

from brainframe.client.ui.resources.paths import qt_ui_paths


class EncodingEntry(QWidget):
    def __init__(self, encoding_class_name: str, parent=None, ):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.encoding_entry_ui, self)

        self.encoding_class_name: QLabel
        self.encoding_class_name.setText(encoding_class_name)

        self._fix_button_width()
        self.delete_button: QPushButton

        # Set this before hiding the button, as the button is taller than the
        # rest of the widget. Not doing this will make this widget height
        # change when the button is hidden/shown
        self.setMinimumHeight(self.sizeHint().height())
        self.delete_button.hide()

    def mouseReleaseEvent(self, event: QMouseEvent):
        print("I was clicked")

    def enterEvent(self, event: QEvent):
        self.delete_button.show()

        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        self.delete_button.hide()

        super().leaveEvent(event)

    def _fix_button_width(self):
        # Set min width of delete button properly
        # https://stackoverflow.com/a/19502467/8134178
        text_size = self.delete_button.fontMetrics().size(
            Qt.TextShowMnemonic,
            self.delete_button.text())
        options = QStyleOptionButton()
        options.initFrom(self.delete_button)
        options.rect.setSize(text_size)
        button_size = self.delete_button.style().sizeFromContents(
            QStyle.CT_PushButton,
            options,
            text_size,
            self.delete_button)
        self.delete_button.setMaximumSize(button_size)
