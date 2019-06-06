from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QStyle, \
    QStyleOptionButton
from PyQt5.uic import loadUi

from brainframe.client.ui.resources.paths import qt_ui_paths


class EncodingEntry(QWidget):
    encoding_entry_clicked_signal = pyqtSignal(str)
    """Emitted when the widget (excluding delete button) is clicked

    Connected to:
    - EncodingList <-- Dynamic
      [parent].encoding_entry_clicked_signal
    """
    delete_encoding_signal = pyqtSignal(str)
    """Emitted when the delete button is pressed
    
    Connected to:
    - EncodingList <-- Dynamic
    [parent].delete_encoding_signal
    """

    def __init__(self, encoding_class_name: str, parent=None, ):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.encoding_entry_ui, self)

        self.encoding_class_name_label: QLabel
        self.encoding_class_name_label.setText(encoding_class_name)
        self.delete_button: QPushButton

        self.encoding_class_name = encoding_class_name

        self.init_ui()
        self.init_slots_and_signals()

    def init_ui(self):
        self._fix_button_width()

        # Set this before hiding the button, as the button is taller than the
        # rest of the widget. Not doing this will make this widget height
        # change when the button is hidden/shown
        self.setMinimumHeight(self.sizeHint().height())
        self.delete_button.hide()

    def init_slots_and_signals(self):
        # noinspection PyUnresolvedReferences
        self.delete_button.clicked.connect(
            lambda: self.delete_encoding_signal.emit(self.encoding_class_name))

    def mouseReleaseEvent(self, event: QMouseEvent):
        # noinspection PyUnresolvedReferences
        self.encoding_entry_clicked_signal.emit(self.encoding_class_name)

    def enterEvent(self, event: QEvent):
        self.delete_button.show()

        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        self.delete_button.hide()

        super().leaveEvent(event)

    def _fix_button_width(self):
        """Set min width of delete button properly

        # https://stackoverflow.com/a/19502467/8134178
        """
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
