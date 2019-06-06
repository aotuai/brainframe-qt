from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from brainframe.client.api import api
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

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.identity_grid_ui, self)

        self.setLayout(IdentityGridLayout())

        self.init_identities()

    def init_identities(self):
        identities = api.get_identities()
        self.add_identities(identities)

    def add_identities(self, identities):
        for identity in identities:
            identity = IdentityEntry(identity, self)
            identity.identity_clicked_signal.connect(
                self.identity_clicked_signal)

            self.layout().addWidget(identity)

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
        # TODO: Wait for API to support this
        print("Filter request received")
