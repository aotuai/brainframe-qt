from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

from brainframe.client.api.codecs import Identity
from brainframe.client.ui.resources.paths import qt_ui_paths

from .identity_info import IdentityInfo


class IdentityConfiguration(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.identity_configuration_ui2, self)

        self.identity_info: IdentityInfo
        self.identity_info.hide()

    @classmethod
    def show_dialog(cls):
        dialog = cls()
        dialog.exec_()

    @pyqtSlot(object)
    def show_identity_info_slot(self, identity: Identity):
        """Shows the information for an identity.

        Connected to:
        - IdentityGrid -- QtDesigner
          self.identity_grid.identity_clicked
        """
        self.identity_info.init_identity(identity)
