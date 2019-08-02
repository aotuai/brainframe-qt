import logging
import os
import sys
import traceback

from requests.exceptions import ConnectionError

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QSizePolicy, \
    QSpacerItem, QTextEdit


class StandardError(QMessageBox):
    """Standard error popup dialog

    This does not use a .ui file because QtDesigner does not have support for
    QMessageBox widgets
    """

    def __init__(self, exc_type, exc_obj, exc_tb, close_client=False,
                 parent=None):
        super().__init__(parent=parent)

        self._init_text(exc_type, exc_obj, exc_tb, close_client=close_client)
        self._init_ui(close_client)

    @classmethod
    def show_error(cls, exc_type, exc_obj, exc_tb, close_client=False):
        # Ignore false exceptions thrown during init of QtDesigner
        if cls._is_qt_designer_init_error(exc_obj):
            return

        dialog = cls(exc_type, exc_obj, exc_tb, close_client=close_client)
        dialog.exec_()

    def _init_text(self, exc_type, exc_obj, exc_tb, close_client=False):

        tb_message = traceback.format_exception(
            exc_type, exc_obj, exc_tb)

        tb_message_text = "".join(tb_message[:-1])
        tb_message_info = tb_message[-1].rstrip()

        self.setWindowTitle(self.tr("An exception has occurred"))
        if exc_type is ConnectionError:
            text = self.tr("Connection to server lost. Client must be closed")
            self.setText(text)
        else:
            # Only show info if the connection was not closed. This makes the
            # dialog a little clearer
            text = self.tr("An exception has occurred.")
            if close_client:
                text += " " + self.tr("The client must be closed.")
            self.setText(text)
            self.setInformativeText(tb_message_info)

        self.setDetailedText(tb_message_text)

        log_func = logging.critical if close_client else logging.error

        # Log exception as well as show it to user
        log_func(tb_message_info)
        log_func(tb_message_text)

    def _init_ui(self, close_client=False):
        self.setIcon(QMessageBox.Critical)
        self.setTextFormat(Qt.RichText)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Add the traceback for the exception to the dialog
        self._create_traceback_view()

        # Button to allow user to copy exception to clipboard
        copy_button = self.addButton(self.tr("Copy to Clipboard"),
                                     QMessageBox.ActionRole)
        copy_button.disconnect()
        # noinspection PyUnresolvedReferences
        copy_button.clicked.connect(self.copy_to_clipboard)

        # Button that forces the client to close
        if close_client:
            close_button = self.addButton(self.tr("Close Client"),
                                          QMessageBox.DestructiveRole)
            # noinspection PyUnresolvedReferences
            close_button.clicked.connect(self.close_client)
            self.setStandardButtons(QMessageBox.NoButton)

        else:
            close_button = QMessageBox.Close

            # https://stackoverflow.com/questions/7543258/adding-detailed-text-in-qmessagebox-makes-close-x-button-disabled
            self.setStandardButtons(QMessageBox.Close)

        self.setDefaultButton(close_button)
        self.setEscapeButton(close_button)

    def _create_traceback_view(self):
        """Add the traceback for the exception to the dialog"""
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
        try:
            self.findChildren(QTextEdit)[0].setFixedHeight(200)
        except IndexError:
            # Why is this exception raised when QtDesigner has another
            # Exception during its initialization
            pass

    def copy_to_clipboard(self):
        """Copy the error's text to the system clipboard"""
        clipboard = QApplication.clipboard()

        clipboard_text = (f"{self.informativeText()}\n\n"
                          f"{self.detailedText()}")

        clipboard.setText(clipboard_text)

        logging.info(self.tr("Error copied to clipboard"))

    @staticmethod
    def close_client():
        logging.info(QApplication.translate("StandardError", "Quitting"))

        # TODO: Why does QApplication.exit not work
        QApplication.exit(-1)

        # TODO: Should not be necessary but QApplication.exit doesn't work
        # noinspection PyProtectedMember
        os._exit(-1)

    @staticmethod
    def _is_qt_designer_init_error(exc_obj):

        # This environment variable is only set when running QtDesigner
        if os.getenv("PYQTDESIGNERPATH"):
            return True

        # Ignore this specific error
        ignore = "super-class __init__() of type BasePlugin was never called"
        return str(exc_obj) == ignore
