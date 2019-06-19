from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QLineEdit
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths
from brainframe.client.ui.resources import QTAsyncWorker

from ..encoding_list import EncodingList


class IdentitySearchFilter(QWidget):
    filter_by_encoding_class_signal = pyqtSignal(str)
    """Emitted when it is desired to filter by an encoding class name
    
    Connected to:
    - EncodingList --> QtDesigner
      self.encoding_list.encoding_entry_selected_signal
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
        self.encoding_list.setContentsMargins(0, 9, 0, 9)

    def init_encoding_list(self):

        def func():
            plugins = api.get_plugins()

            # Get names of all classes that encodable
            encoding_class_names = set()
            for plugin in plugins:
                output_type = plugin.output_type
                if not output_type.encoded:
                    continue
                encoding_class_names.update(output_type.detections)

            encoding_class_names.update(api.get_encoding_class_names())

            return encoding_class_names

        def callback(encoding_class_names):
            self.encoding_list.init_encodings(encoding_class_names)

        QTAsyncWorker(self, func, callback).start()

    @pyqtSlot(str)
    def delete_encoding_class_slot(self, encoding_class: str):
        """Delete event encoding of a class type from all identities on the
        database"""

        self.encoding_list: EncodingList

        def func():
            api.delete_encodings(class_name=encoding_class)

        def callback(_):
            # Refresh the encoding class list. The one we just deleted could be
            # gone if there is no corresponding encoder plugin loaded
            self.init_encoding_list()

            # Tell the grid to not filter by anything anymore
            # noinspection PyUnresolvedReferences
            self.filter_by_encoding_class_signal.emit("")

        QTAsyncWorker(self, func, callback).start()
