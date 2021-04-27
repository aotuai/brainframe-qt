import logging
from typing import Optional, Tuple

from PyQt5.QtCore import QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QCheckBox, QDialog, QDialogButtonBox, \
    QGridLayout, QLabel, QLineEdit, QPushButton, QWidget
from PyQt5.uic import loadUi

from brainframe.api import BrainFrameAPI, bf_codecs, bf_errors

from brainframe_qt.api_utils import api
from brainframe_qt.extensions import DialogActivity
from brainframe_qt.ui.dialogs.license_dialog.license_dialog import \
    LicenseDialog
from brainframe_qt.ui.resources import QTAsyncWorker
from brainframe_qt.ui.resources.config.server_config import QSettingsServerConfig
from brainframe_qt.ui.resources.links.documentation import \
    LICENSE_DOCS_LINK
from brainframe_qt.ui.resources.paths import qt_ui_paths
from brainframe_qt.ui.resources.ui_elements.widgets.dialogs import \
    BrainFrameMessage
from brainframe_qt.util.secret import decrypt, encrypt


class ServerConfigActivity(DialogActivity):
    _built_in = True

    def open(self, *, parent: QWidget):
        ServerConfigurationDialog.show_dialog(parent=parent)

    def window_title(self) -> str:
        return QApplication.translate("ServerConfigActivity",
                                      "Server Configuration")

    @staticmethod
    def icon() -> QIcon:
        return QIcon(":/icons/server_config")

    @staticmethod
    def short_name() -> str:
        return QApplication.translate("ServerConfigActivity", "Server")


class ServerConfigurationDialog(QDialog):

    def __init__(self, *, parent: QObject):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.server_configuration_ui, self)

        self.server_config: QSettingsServerConfig = (
            QApplication.instance().server_config
        )

        self._init_ui()

    def _init_ui(self):
        self.grid_layout: QGridLayout

        self.server_address_line_edit: QLineEdit
        self.authentication_checkbox: QCheckBox
        self.server_username_line_edit: QLineEdit
        self.server_password_line_edit: QLineEdit
        self.save_password_checkbox: QCheckBox
        self.button_box: QDialogButtonBox
        self.license_config_button: QPushButton

        self.connection_status_label: QLabel
        self.connection_report_label: QLabel
        self.check_connection_button: QPushButton

        self.connection_report_label.setOpenExternalLinks(True)

        self.server_address_line_edit.setText(self.server_config.server_url)
        self.server_username_line_edit.setText(self.server_config.server_username)

        if self.server_config.server_password:
            settings_password = self.server_config.server_password
            if settings_password:
                try:
                    decrypt_password = decrypt(settings_password)
                    self.server_password_line_edit.setText(decrypt_password)
                except ValueError:
                    message = self.tr(
                        "Invalid password saved in QSettings. Clearing.")
                    logging.error(message)
                    try:
                        del self.server_config.server_password
                    except AttributeError:
                        pass

        use_auth = bool(self.server_config.server_username)
        self._show_authentication_fields(use_auth)
        self.authentication_checkbox.setChecked(use_auth)

        self.save_password_checkbox.setChecked(bool(self.server_password))

        # noinspection PyUnresolvedReferences
        self.authentication_checkbox.stateChanged.connect(
            self._show_authentication_fields)
        self.authentication_checkbox.stateChanged.connect(
            self._verify)
        # noinspection PyUnresolvedReferences
        self.server_address_line_edit.textChanged.connect(self._verify)
        # noinspection PyUnresolvedReferences
        self.server_username_line_edit.textChanged.connect(self._verify)
        # noinspection PyUnresolvedReferences
        self.server_password_line_edit.textChanged.connect(self._verify)

        self.license_config_button.clicked.connect(self._open_license_dialog)

        self.check_connection_button.clicked.connect(self.check_connection)

        self._verify()
        if self.fields_filled:
            self.check_connection()

    @property
    def authentication_enabled(self) -> bool:
        return self.authentication_checkbox.isChecked()

    @property
    def credentials(self) -> Optional[Tuple[str, str]]:
        if not self.authentication_enabled:
            return None
        return self.server_username, self.server_password

    @property
    def fields_filled(self) -> bool:
        if not self.server_address:
            return False
        if self.authentication_enabled:
            if not self.server_username:
                return False
            if not self.server_password:
                return False
        return True

    @property
    def save_password(self) -> bool:
        if self.authentication_enabled \
                and self.save_password_checkbox.isChecked():
            return True
        return False

    @property
    def server_address(self) -> str:
        return self.server_address_line_edit.text()

    @property
    def server_password(self) -> Optional[str]:
        if self.authentication_enabled:
            return self.server_password_line_edit.text()
        else:
            return None

    @property
    def server_username(self) -> Optional[str]:
        if self.authentication_enabled:
            return self.server_username_line_edit.text()
        else:
            return None

    def accept(self):

        def _save_settings():
            self.server_config.server_url = self.server_address

            if self.authentication_enabled:
                self.server_config.server_username = self.server_username
                if self.save_password:
                    # Note that this is _not_ meant to be a form of security,
                    # simply to prevent the password from sitting in plain text
                    # on the client computer. The key is available in plain text
                    # within this repo.
                    encrypted = encrypt(self.server_password)
                    self.server_config.server_password = encrypted
            if not self.authentication_enabled or not self.save_password:
                try:
                    del self.server_config.server_password
                except AttributeError:
                    pass

            self.server_config.save_to_disk()

        try:
            api.set_url(self.server_address)
        except ValueError:
            title = self.tr("Invalid Schema")
            message = self.tr(
                "Unable to connect to a BrainFrame server with the provided "
                "URL schema. Supported schemas are {0} and {1}.") \
                .format("http://", "https://")
        else:
            api.set_credentials(self.credentials)

            try:
                api.version()
            except bf_errors.UnauthorizedError:
                title = self.tr("Server Authentication Error")
                message = self.tr(
                    "Unable to authenticate with the BrainFrame server. \n"
                    "Please recheck the entered credentials.")
            except bf_errors.ServerNotReadyError:
                title = self.tr("Connection Error")
                message = self.tr(
                    "Unable to connect to the BrainFrame server. \n"
                    "Please recheck the entered server address.")
            else:
                _save_settings()
                super().accept()
                return

        message = BrainFrameMessage.warning(
            parent=self,
            title=title,
            warning=message
        )
        message.add_button(standard_button=BrainFrameMessage.Ignore)
        result = message.exec()

        if result == BrainFrameMessage.Ignore:
            _save_settings()
            super().accept()

    @classmethod
    def show_dialog(cls, *, parent: QObject):
        cls(parent=parent).exec()

    def check_connection(self):

        def on_success(license_state: bf_codecs.LicenseInfo.State):

            self.license_config_button.setEnabled(True)

            license_link = "<br>"
            license_link += self.tr(
                "<a href='{license_docs_link}'>Download</a> a new one") \
                .format(license_docs_link=LICENSE_DOCS_LINK)

            if license_state is bf_codecs.LicenseInfo.State.EXPIRED:
                label_text = "❗"
                report_text = self.tr("Expired License")
                report_text += license_link
            elif license_state is bf_codecs.LicenseInfo.State.INVALID:
                label_text = "❗"
                report_text = self.tr("Invalid License")
                report_text += license_link
            elif license_state is bf_codecs.LicenseInfo.State.MISSING:
                label_text = "❗"
                report_text = self.tr("Missing License")
                report_text += license_link
            elif license_state is bf_codecs.LicenseInfo.State.VALID:
                label_text = "✔️"
                report_text = self.tr("Connection Successful")
            else:
                label_text = "❗"
                report_text = self.tr("Unknown license state")

            self.connection_status_label.setText(label_text)
            self.connection_report_label.setText(report_text)

        def on_error(exc: BaseException):

            self.license_config_button.setDisabled(True)

            if isinstance(exc, bf_errors.UnauthorizedError):
                label_text = "❗"
                report_text = self.tr("Invalid credentials")
            elif isinstance(exc, bf_errors.ServerNotReadyError):
                label_text = "❌"
                report_text = self.tr("Unable to locate server")
            else:
                raise exc

            self.connection_status_label.setText(label_text)
            self.connection_report_label.setText(report_text)

        QTAsyncWorker(self, self._check_connection,
                      on_success=on_success, on_error=on_error) \
            .start()

    def _check_connection(self) -> bf_codecs.LicenseInfo.State:
        # Create a temporary API object to check connection with
        temp_api = BrainFrameAPI(self.server_address, self.credentials)

        # Check connection
        temp_api.version()

        # Check license state
        license_state = temp_api.get_license_info().state

        return license_state

    def _open_license_dialog(self):
        LicenseDialog.show_dialog(self)
        self.check_connection()

    def _verify(self):

        self.connection_status_label.setText("❓")
        self.connection_report_label.setText("")

        enabled = self.fields_filled
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(enabled)
        self.check_connection_button.setEnabled(enabled)

    def _show_authentication_fields(self, show: bool):

        widgets = [self.server_username_label, self.server_username_line_edit,
                   self.server_password_label, self.server_password_line_edit,
                   self.save_password_checkbox]

        for widget in widgets:
            widget.setVisible(show)
