import logging

from requests.exceptions import ConnectionError

from PyQt5.QtWidgets import QDialog, QLineEdit, QCheckBox, QDialogButtonBox, \
    QMessageBox
from PyQt5.uic import loadUi

from brainframe.client.api_helpers import api
from brainframe.api import api_errors
from brainframe.client.ui.resources import settings
from brainframe.client.ui.resources.paths import qt_ui_paths
from brainframe.shared.secret import decrypt, encrypt


class ServerConfigurationDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.server_configuration_ui, self)

        self._init_ui()

    def _init_ui(self):
        self.server_address_line_edit: QLineEdit
        self.authentication_checkbox: QCheckBox
        self.server_username_line_edit: QLineEdit
        self.server_password_line_edit: QLineEdit
        self.save_password_checkbox: QCheckBox
        self.button_box: QDialogButtonBox

        self.server_address_line_edit.setText(settings.server_url.val())
        self.server_username_line_edit.setText(settings.server_username.val())

        if settings.server_password:
            settings_password = settings.server_password.val()
            if settings_password:
                try:
                    decrypt_password = decrypt(settings_password)
                    self.server_password_line_edit.setText(decrypt_password)
                except ValueError:
                    message = self.tr(
                        "Invalid password saved in QSettings. Clearing.")
                    logging.error(message)
                    settings.server_password.delete()

        use_auth = bool(settings.server_username.val())
        self._show_authentication_fields(use_auth)
        self.authentication_checkbox.setChecked(use_auth)

        # noinspection PyUnresolvedReferences
        self.authentication_checkbox.stateChanged.connect(
            self._show_authentication_fields)
        # noinspection PyUnresolvedReferences
        self.server_address_line_edit.textChanged.connect(self._verify)
        # noinspection PyUnresolvedReferences
        self.server_username_line_edit.textChanged.connect(self._verify)
        # noinspection PyUnresolvedReferences
        self.server_password_line_edit.textChanged.connect(self._verify)
        # noinspection PyUnresolvedReferences
        self.save_password_checkbox.stateChanged.connect(self._verify)

    def accept(self):

        server_address = self.server_address_line_edit.text()
        server_auth: bool = self.authentication_checkbox.isChecked()
        server_username = self.server_username_line_edit.text()
        server_password = self.server_password_line_edit.text()
        save_password = self.save_password_checkbox.isChecked()

        def _save_settings():
            settings.server_url.set(server_address)
            settings.server_username.set(server_username)

            if server_auth and save_password:
                encrypted = encrypt(server_password)
                settings.server_password.set(encrypted)
            else:
                settings.server_password.delete()

        try:
            api.set_url(server_address)
        except ValueError:
            title = self.tr("Invalid Schema")
            message = self.tr(
                "Unable to connect to a BrainFrame server with the provided "
                "URL schema. Supported schemas are {0} and {1}.") \
                .format("http://", "https://")
        else:
            if server_auth:
                api.set_credentials((server_username, server_password))
            else:
                api.set_credentials(None)

            try:
                api.version()
            except api_errors.UnauthorizedError:
                title = self.tr("Server Authentication Error")
                message = self.tr(
                    "Unable to authenticate with the BrainFrame server. \n"
                    "Please recheck the entered credentials.")
            except ConnectionError:
                title = self.tr("Connection Error")
                message = self.tr(
                    "Unable to connect to the BrainFrame server. \n"
                    "Please recheck the entered server address.")
            else:
                _save_settings()
                super().accept()
                return

        buttons = QMessageBox.Ok | QMessageBox.Ignore

        result = QMessageBox.warning(self, title, message, buttons)

        if result == QMessageBox.Ignore:
            _save_settings()
            super().accept()

    @classmethod
    def show_dialog(cls, parent):
        cls(parent=parent).exec()

    def _verify(self):
        """Make sure that the ok button should be enabled"""

        server_address = self.server_address_line_edit.text()
        server_auth: bool = self.authentication_checkbox.isChecked()
        server_username = self.server_username_line_edit.text()
        server_password = self.server_password_line_edit.text()

        self.button_box: QDialogButtonBox

        enabled = True

        if not server_address:
            enabled = False
        if server_auth:
            if not server_username:
                enabled = False
            if not server_password:
                enabled = False

        self.button_box.button(QDialogButtonBox.Ok).setEnabled(enabled)

    def _show_authentication_fields(self, show: bool):

        widgets = [self.server_username_label, self.server_username_line_edit,
                   self.server_password_label, self.server_password_line_edit,
                   self.save_password_checkbox]

        for widget in widgets:
            widget.setVisible(show)
