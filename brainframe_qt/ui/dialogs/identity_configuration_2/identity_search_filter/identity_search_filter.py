from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths

from ..encoding_list import EncodingList


class IdentitySearchFilter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.identity_search_filter_ui, self)

        self.encoding_list: EncodingList

        self.init_encoding_list()

    def init_encoding_list(self):
        plugins = api.get_plugins()

        encodings = []
        for plugin in plugins:
            output_type = plugin.output_type
            if not output_type.encoded:
                continue
            encodings.extend(output_type.detections)

        self.encoding_list.init_encodings(encodings)
