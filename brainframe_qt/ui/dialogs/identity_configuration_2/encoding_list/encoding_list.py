from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from brainframe.client.ui.resources.paths import qt_ui_paths

from .encoding_entry import EncodingEntry


class EncodingList(QWidget):
    def __init__(self, parent=None, encodings=()):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.encoding_list_ui, self)

        if encodings:
            self.init_encodings(encodings)

    def init_encodings(self, encodings):
        for encoding in encodings:
            self._add_encoding(encoding)

    def clear_encodings(self):
        for index in reversed(range(self.layout().count())):
            self.layout().takeAt(index)

    def _add_encoding(self, encoding: str):
        encoding_entry = EncodingEntry(encoding, self)
        self.layout().addWidget(encoding_entry)

    def remove_encoding(self, encoding):
        pass
