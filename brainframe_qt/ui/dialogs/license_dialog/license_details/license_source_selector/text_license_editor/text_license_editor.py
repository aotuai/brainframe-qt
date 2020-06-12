from PyQt5.QtWidgets import QMessageBox, QWidget

from brainframe.api import bf_codecs, bf_errors
from brainframe.client.api_utils import api
from brainframe.client.ui.resources import QTAsyncWorker
from .text_license_editor_ui import _TextLicenseEditorUI


LICENSE_DOCS_LINK = "https://aotu.ai/docs/user_guide/server_setup/" \
                    "#getting-a-license"


class TextLicenseEditor(_TextLicenseEditorUI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_signals()

    def _init_signals(self) -> None:
        self.license_textbox.textChanged.connect(self._handle_text_change)
        self.update_license_button.clicked.connect(self.update_license)

    def update_license(self):

        def on_success(license_info: bf_codecs.LicenseInfo):
            print(license_info)

        license_key = self.license_textbox.toPlainText()
        QTAsyncWorker(self, api.set_license_key, f_args=(license_key, ),
                      on_success=on_success,
                      on_error=self._handle_update_license_error) \
            .start()

    def _handle_text_change(self):
        text = self.license_textbox.toPlainText()
        self.update_license_button.setDisabled(text == "" or text.isspace())

    def _handle_update_license_error(self, exc: BaseException):
        if isinstance(exc, bf_errors.LicenseInvalidError):

            message_title = self.tr("Invalid License Format")
            message = self.tr(
                "The provided license has an invalid format. Please "
                "<a href='{license_docs_link}'>download a new license</a>.") \
                .format(license_docs_link=LICENSE_DOCS_LINK)
        else:
            raise exc

        QMessageBox.information(self, message_title, message)
