import logging
import os
import traceback

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMessageBox,
    QSizePolicy,
    QSpacerItem,
    QTextEdit
)


class StandardError(QMessageBox):
    """Standard error popup dialog

    This does not use a .ui file because QtDesigner does not have support for
    QMessageBox widgets
    """

    def __init__(self, exc_type, exc_obj, exc_tb, parent=None):
        super().__init__(parent=parent, )

        self._init_text(exc_type, exc_obj, exc_tb)
        self._init_ui()

    @classmethod
    def show_error(cls, exc_type, exc_obj, exc_tb):

        # Ignore false exceptions thrown during init of QtDesigner
        if cls._is_qt_designer_init_error(exc_obj):
            return

        dialog = cls(exc_type, exc_obj, exc_tb)
        dialog.exec_()

    def _init_ui(self):
        self.setIcon(QMessageBox.Critical)
        self.setTextFormat(Qt.RichText)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Trick to set the width of the message dialog
        # http://www.qtcentre.org/threads/22298-QMessageBox-Controlling-the-width
        # noinspection PyArgumentList
        self.layout().addItem(
            QSpacerItem(600, 0, QSizePolicy.Minimum, QSizePolicy.Expanding),
            self.layout().rowCount(),
            0, 1,
            self.layout().columnCount())

        # Force detailed view taller to show traceback better
        # https://stackoverflow.com/a/48590647/8134178
        self.findChildren(QTextEdit)[0].setFixedHeight(200)

        # https://stackoverflow.com/questions/7543258/adding-detailed-text-in-qmessagebox-makes-close-x-button-disabled
        self.setStandardButtons(QMessageBox.Close)
        self.setDefaultButton(QMessageBox.Close)
        self.setEscapeButton(QMessageBox.Close)

        copy_button = self.addButton("Copy to Clipboard",
                                     QMessageBox.ActionRole)
        copy_button.disconnect()
        # noinspection PyUnresolvedReferences
        copy_button.clicked.connect(self.copy_to_clipboard)

    def _init_text(self, exc_type, exc_obj, exc_tb):
        self.setWindowTitle("An exception has occurred")
        self.setText("An exception has occurred")

        tb_message = traceback.format_exception(
            exc_type, exc_obj, exc_tb)

        tb_message_text = "".join(tb_message[:-1])
        tb_message_info = tb_message[-1].rstrip()

        self.setInformativeText(tb_message_info)
        self.setDetailedText(tb_message_text)

        # Log warning as well as show it to user
        logging.error(tb_message_info)
        logging.error(tb_message_text)

    def copy_to_clipboard(self):
        """Copy the error's text to the system clipboard"""
        clipboard = QApplication.clipboard()

        clipboard_text = (f"{self.informativeText()}\n\n"
                          f"{self.detailedText()}")

        clipboard.setText(clipboard_text)

        logging.info("Error copied to clipboard")

    @staticmethod
    def _is_qt_designer_init_error(exc_obj):
        # This environment variable is only set when running QtDesigner
        if not os.getenv("PYQTDESIGNERPATH"):
            return

        # Ignore this specific error
        ignore = "super-class __init__() of type BasePlugin was never called"
        if str(exc_obj) == ignore:
            return True
