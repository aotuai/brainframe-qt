from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QLineEdit
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths

from ..encoding_list import EncodingList


class IdentitySearchFilter(QWidget):
    filter_by_encoding_class_signal = pyqtSignal(str)
    """Emitted when it is desired to filter by an encoding class name
    
    Connected to:
    - EncodingList --> QtDesigner
      self.encoding_list.encoding_entry_clicked_signal
    - IdentityGrid <-- QtDesigner
      [peer].filter_by_encoding_class_slot
    """
    filter_by_search_string_signal = pyqtSignal(str)
    """Emitted whenever the contents of the search QLineEdit change
    
    Connected to:
    - QLineEdit --> Dynamic
      self.search_line_edit.textChanged
    - IdentityGrid <-- QtDesigner
      [peer].filter_by_search_slot
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.identity_search_filter_ui, self)

        self.encoding_list: EncodingList
        self.search_line_edit: QLineEdit

        self.init_ui()

        self.init_encoding_list()

    def init_ui(self):
        self.search_line_edit.setContentsMargins(10, 5, 10, 5)
        self.encoding_list.setContentsMargins(9, 9, 9, 9)

    def init_encoding_list(self):
        plugins = api.get_plugins()

        # Get names of all classes that encodable
        encoding_class_names = []
        for plugin in plugins:
            output_type = plugin.output_type
            if not output_type.encoded:
                continue
            encoding_class_names.extend(output_type.detections)

        encoding_class_names.extend(api.get_encoding_class_names())

        self.encoding_list.init_encodings(encoding_class_names)
