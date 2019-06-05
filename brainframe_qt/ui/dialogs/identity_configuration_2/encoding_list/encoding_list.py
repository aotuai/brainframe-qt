from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.uic import loadUi

from brainframe.client.ui.resources.paths import qt_ui_paths

from .encoding_entry import EncodingEntry


class EncodingList(QWidget):
    def __init__(self, parent=None, encodings=()):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.encoding_list_ui, self)

        self.encoding_list_layout: QVBoxLayout

        if encodings:
            self.init_encodings(encodings)

    def init_encodings(self, encodings):
        self.clear_encodings()
        for encoding in encodings:
            self.add_encoding(encoding)

    def clear_encodings(self):
        for index in reversed(range(self.encoding_list_layout.count())):
            encoding_item = self.encoding_list_layout.takeAt(index)
            encoding_item.widget().deleteLater()

    def add_encoding(self, encoding: str):
        encoding_entry = EncodingEntry(encoding, self)
        self.encoding_list_layout.addWidget(encoding_entry)

    def remove_encoding(self, encoding):
        raise NotImplementedError
