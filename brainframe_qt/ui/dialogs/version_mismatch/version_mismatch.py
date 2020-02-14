import os
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from brainframe.client.ui.dialogs import dialog_actions


class VersionMismatch(QMessageBox):
    """Shown when there is a version mismatch between the client and server."""

    def __init__(self, server_version, client_version, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle(self.tr("Version Mismatch"))
        self.setIcon(QMessageBox.Critical)
        self.setTextFormat(Qt.RichText)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)

        message = ("The server is using version {server_version} but this "
                   "client is on version {client_version}. Please download "
                   "the matching version of the client at {download_url}.")
        message = self.tr(message).format(
            server_version=server_version,
            client_version=client_version,
            download_url="https://dilililabs.com/docs/downloads/")
        self.setText(message)

        close_button = self.addButton(self.tr("Close Client"),
                                      QMessageBox.DestructiveRole)
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(dialog_actions.close_client)

        self.setStandardButtons(QMessageBox.NoButton)
        self.setDefaultButton(close_button)
        self.setEscapeButton(close_button)
