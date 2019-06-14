from typing import List

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimerEvent
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.api.codecs import Identity
from brainframe.client.ui.resources.paths import qt_ui_paths

from .identity_entry import IdentityEntry
from .identity_grid_layout import IdentityGridLayout


class IdentityGrid(QWidget):
    identity_clicked_signal = pyqtSignal(object)
    """Emitted whenever an IdentityEntry is clicked (passthrough)

    Connected to:
    - IdentityEntry --> Dynamic
      [child].identity_clicked_signal
    - IdentityInfo <-- QtDesigner
      [peer].show_identity_info_slot
    """
    identity_load_started_signal = pyqtSignal()
    """Emits when identities are loading
    
    Connected to:
    - IdentityConfiguration <-- Dynamic
      [parent].[lambda]
    """
    identity_load_progress_signal = pyqtSignal(int, int)
    """Emits percent of identities that have been uploaded so far
    
    Connected to:
    - IdentityConfiguration <-- Dynamic
      [parent].[lambda]
    """
    identity_load_finished_signal = pyqtSignal()
    """Emits when identities are done loading
    
    Connected to:
    - IdentityConfiguration <-- Dynamic
      [parent].[lambda]
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.identity_grid_ui, self)

        self.setLayout(IdentityGridLayout())

        self._identities_to_add: List[Identity] = []
        # Stores total number of identities that are to be loading. Also used
        # as a check to see if we're known to be uploading
        self._to_upload = 0
        self.startTimer(0)

        self.init_identities()

    def init_identities(self):
        identities = api.get_identities()
        self.add_identities(identities)

    def timerEvent(self, timer_event: QTimerEvent):
        if not self._identities_to_add:
            return

        # Signal start of loading
        if self._to_upload == 0:
            self._to_upload = len(self._identities_to_add)
            # noinspection PyUnresolvedReferences
            self.identity_load_started_signal.emit()

        identity = self._identities_to_add.pop()
        identity_entry = IdentityEntry(identity, self)
        identity_entry.identity_clicked_signal.connect(
            self.identity_clicked_signal)
        self.layout().addWidget(identity_entry)

        # Signal load progress
        uploaded_so_far = self._to_upload - len(self._identities_to_add)
        # noinspection PyUnresolvedReferences
        self.identity_load_progress_signal.emit(
            uploaded_so_far, self._to_upload)

        # Signal end of uploading
        if not self._identities_to_add:
            self._to_upload = 0
            # noinspection PyUnresolvedReferences
            self.identity_load_finished_signal.emit()

    def add_identities(self, identities):
        self._identities_to_add.extend(identities)

    def clear_identities(self):
        for index in reversed(range(self.layout().count())):
            widget = self.layout().takeAt(index).widget()
            widget.deleteLater()

    @pyqtSlot(str)
    def filter_by_encoding_class_slot(self, encoding_class: str):
        """
        Called when we want to only show encodings of a specific class type.

        If encoding_class is an empty string, all encoding class types will be
        shown
        """
        self.clear_identities()

        identities = api.get_identities(encoded_for_class=encoding_class)
        self.add_identities(identities)
