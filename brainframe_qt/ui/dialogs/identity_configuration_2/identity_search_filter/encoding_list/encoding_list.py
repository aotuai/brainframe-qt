from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths

from .encoding_entry import EncodingEntry


class EncodingList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.encoding_list_ui, self)

        self.init_encodings()

    def init_encodings(self):

        plugins = api.get_plugins()

        encodings = []
        for plugin in plugins:
            output_type = plugin.output_type
            if not output_type.encoded:
                continue
            encodings.extend(output_type.detections)

        for encoding in encodings:
            self._add_encoding(encoding)

    def _add_encoding(self, encoding: str):
        encoding_entry = EncodingEntry(encoding, self)
        self.layout().addWidget(encoding_entry)
