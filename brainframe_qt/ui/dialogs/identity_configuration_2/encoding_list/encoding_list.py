from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.uic import loadUi

from brainframe.client.ui.resources.paths import qt_ui_paths

from .encoding_entry import EncodingEntry


class EncodingList(QWidget):
    encoding_entry_clicked_signal = pyqtSignal(str)
    """Emitted when a child EncodingEntry is clicked

    Connected to:
    - EncodingEntry --> Dynamic
      [child].encoding_entry_clicked_signal
    - IdentitySearchFilter <-- Dynamic
      [parent].filter_by_encoding_class_signal
    """

    def __init__(self, parent=None, encodings=()):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.encoding_list_ui, self)
        self.init_ui()

        self.encoding_list_layout: QVBoxLayout
        self.none_label: QLabel

        if encodings:
            self.init_encodings(encodings)

    def init_ui(self):
        # Make [None] label use alt text color from theme
        palette = self.none_label.palette()
        text_color = palette.placeholderText().color()
        palette.setColor(QPalette.WindowText, text_color)
        self.none_label.setPalette(palette)

    def init_encodings(self, encodings):
        self.clear_encodings()
        for encoding in encodings:
            self.add_encoding(encoding)

    def clear_encodings(self):
        for index in reversed(range(self.encoding_list_layout.count())):
            encoding_item = self.encoding_list_layout.takeAt(index)
            encoding_item.widget().deleteLater()
        self.none_label.show()

    def add_encoding(self, encoding: str):
        encoding_entry = EncodingEntry(encoding, self)
        encoding_entry.encoding_entry_clicked_signal.connect(
            self.encoding_entry_clicked_signal)
        self.encoding_list_layout.addWidget(encoding_entry)
        self.none_label.hide()

    def remove_encoding(self, encoding):
        raise NotImplementedError
