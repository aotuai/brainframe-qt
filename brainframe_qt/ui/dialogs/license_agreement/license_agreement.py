import hashlib

from PyQt5.QtWidgets import QBoxLayout, QDialog, QDialogButtonBox
from PyQt5.uic import loadUi

from brainframe.client.ui.resources import settings
from brainframe.client.ui.resources.paths import qt_ui_paths, text_paths


class EULADialog(QDialog):
    """License agreement that a customer must agree to before using software"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.license_agreement_ui, self)
        self.button_box.addButton(self.tr("Decline"),
                                  QDialogButtonBox.RejectRole)
        self.button_box.addButton(self.tr("Accept"),
                                  QDialogButtonBox.AcceptRole)

        # Reverse the order of the buttons to be standard (accept on left)
        self.button_box.layout().setDirection(QBoxLayout.RightToLeft)

        self.text = self.get_text_from_file(text_paths.eula_txt)
        self.license_text.setPlainText(self.text)

    @classmethod
    def get_agreement(cls, parent):

        dialog = cls(parent)
        license_md5 = hashlib.md5(dialog.text.encode('utf-8')).hexdigest()

        # Check if the license was already agreed to
        license_accepted = settings.client_license_accepted.val()
        license_accepted_md5 = settings.client_license_md5.val()

        if license_accepted:
            # Ensure that the license agreed to was the current version
            if license_accepted_md5 == license_md5:
                return True

        # License has not been accepted. Prompt user
        result = dialog.exec_()

        settings.client_license_accepted.set(result)
        settings.client_license_md5.set(license_md5)

        return result

    @staticmethod
    def get_text_from_file(path):
        """Get text from path as a string"""
        with open(path) as fi:
            text = fi.read()
        return text
