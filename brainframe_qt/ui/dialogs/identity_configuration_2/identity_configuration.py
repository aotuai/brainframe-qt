from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

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
