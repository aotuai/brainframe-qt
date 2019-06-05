from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths

from .identity_entry import IdentityEntry
from .identity_grid_layout import IdentityGridLayout


class IdentityGrid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.identity_grid_ui, self)

        self.setLayout(IdentityGridLayout())

        self.init_identities()

    def init_identities(self):
        _ = self
        identities = api.get_identities()

        for identity in identities:
            identity = IdentityEntry(identity, self)
            self.layout().addWidget(identity)
