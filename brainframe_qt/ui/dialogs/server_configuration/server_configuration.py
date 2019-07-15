from PyQt5.QtWidgets import QDialog, QLineEdit
from PyQt5.uic import loadUi

from brainframe.client.ui.resources import settings
from brainframe.client.ui.resources.paths import qt_ui_paths


class ServerConfigurationDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.server_configuration_ui, self)

        self.server_address_line_edit: QLineEdit
        self.server_address_line_edit.setText(settings.server_url.val())

    @classmethod
    def show_dialog(cls, parent):

        dialog = cls(parent=parent)

        result = dialog.exec()
        if not result:
            return

        settings.server_url.set(dialog.server_address_line_edit.text())
