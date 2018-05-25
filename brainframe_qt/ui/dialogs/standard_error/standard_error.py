import traceback

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QSizePolicy, QSpacerItem, QTextEdit


class StandardError(QMessageBox):

    def __init__(self, exc_type, exc_obj, exc_tb, parent=None):
        super().__init__(parent=parent)

        tb_message = traceback.format_exception(
            exc_type, exc_obj, exc_tb)

        tb_message_text = "".join(tb_message[:-1])
        tb_message_info = tb_message[-1]

        self.setWindowTitle("An exception has occurred")
        self.setText("An exception has occurred")

        self.setInformativeText(tb_message_info)
        self.setDetailedText(tb_message_text)
        self.setTextFormat(Qt.RichText)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setIcon(QMessageBox.Critical)

        # Trick to set the width of the message dialog
        # http://www.qtcentre.org/threads/22298-QMessageBox-Controlling-the-width
        # noinspection PyArgumentList
        # Pycharm gets confused
        self.layout().addItem(
            QSpacerItem(600, 0, QSizePolicy.Minimum, QSizePolicy.Expanding),
            self.layout().rowCount(),
            0, 1,
            self.layout().columnCount())

        # Force detailed view taller to show traceback better
        # https://stackoverflow.com/a/48590647/8134178
        self.findChildren(QTextEdit)[0].setFixedHeight(200)

    @classmethod
    def show_error(cls, exc_type, exc_obj, exc_tb):
        dialog = cls(exc_type, exc_obj, exc_tb)
        dialog.exec_()
