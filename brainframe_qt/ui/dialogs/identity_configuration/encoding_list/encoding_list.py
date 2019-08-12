from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.uic import loadUi

from brainframe.client.ui.resources.paths import qt_ui_paths

from .encoding_entry import EncodingEntry


class EncodingList(QWidget):
    encoding_entry_selected_signal = pyqtSignal(str)
    """Emitted when a child EncodingEntry is selected

    Connected to:
    - IdentitySearchFilter <-- Dynamic
      [parent].filter_by_encoding_class_signal
    """
    delete_encoding_class_signal = pyqtSignal(str)
    """Emitted when an encoding entry requests to be deleted

    Connected to:
    - EncodingEntry --> Dynamic
    [child].delete_encoding_class_signal
    - IdentitySearchFilter <-- QtDesigner
    [parent].delete_encoding_class_slot
    - IdentityInfo <-- QtDesigner
    [parent].delete_encoding_class_slot
    """

    def __init__(self, parent=None, encodings=()):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.encoding_list_ui, self)

        self.encoding_list_layout: QVBoxLayout
        self.none_label: QLabel

        self.init_ui()

        self.init_encodings(encodings)

    def init_ui(self):
        # Make [None] label use alt text color from theme
        palette = self.none_label.palette()
        text_color = palette.mid().color()
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
        encoding_entry.encoding_entry_selected_signal.connect(
            self.encoding_entry_selected_slot)
        encoding_entry.delete_encoding_class_signal.connect(
            self.delete_encoding_class_signal)
        self.encoding_list_layout.addWidget(encoding_entry)
        self.none_label.hide()

    def remove_encoding(self, encoding):
        raise NotImplementedError

    @pyqtSlot(bool, str)
    def encoding_entry_selected_slot(self, selected: bool,
                                     encoding_class: str):
        """Called whenever an encoding is selected/deselected

        Connected to:
        - EncodingEntry --> Dynamic
          [child].encoding_entry_selected_signal"""
        if selected:
            for index in range(self.encoding_list_layout.count()):
                item = self.encoding_list_layout.itemAt(index)
                widget: EncodingEntry = item.widget()
                if widget.encoding_class_name != encoding_class:
                    widget.selected = False
        else:
            encoding_class = ""

        # noinspection PyUnresolvedReferences
        self.encoding_entry_selected_signal.emit(encoding_class)
