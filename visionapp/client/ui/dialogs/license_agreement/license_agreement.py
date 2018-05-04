from PyQt5.QtWidgets import QBoxLayout, QDialog, QDialogButtonBox
from PyQt5.QtCore import QSettings
from PyQt5.uic import loadUi

from visionapp.client.ui.resources.paths import qt_ui_paths, text_paths


class LicenseAgreement(QDialog):
    """License agreement that a customer must agree to before using software"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.license_agreement_ui, self)
        self.button_box.addButton("Decline", QDialogButtonBox.RejectRole)
        self.button_box.addButton("Accept", QDialogButtonBox.AcceptRole)

        # Reverse the order of the buttons to be standard (accept on left)
        self.button_box.layout().setDirection(QBoxLayout.RightToLeft)

        QSettings().setValue("client_license_accepted", False)

        text = self.get_text_from_file(text_paths.license_agreement_txt)
        self.license_text.setPlainText(text)

    @classmethod
    def get_agreement(cls):
        dialog = cls()
        result = dialog.exec_()

        QSettings().setValue("client_license_accepted", result)

        return result

    @staticmethod
    def get_text_from_file(path):
        """Get text from path as a string"""
        with open(path) as fi:
            text = fi.read()
        return text
