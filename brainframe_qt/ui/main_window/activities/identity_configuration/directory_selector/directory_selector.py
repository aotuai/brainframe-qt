from pathlib import Path

from PyQt5.QtCore import QStandardPaths, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.uic import loadUi

# noinspection PyUnresolvedReferences
from brainframe.client.ui.resources import qt_resources
from brainframe.client.ui.resources.paths import qt_ui_paths


class DirectorySelector(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.directory_selector_ui, self)

        # Set the alert icon on the left of the log entry
        self.select_directory_button.setText("")
        pixmap = QPixmap(":/icons/folder")
        pixmap = pixmap.scaled(32, 32, transformMode=Qt.SmoothTransformation)
        self.select_directory_button.setIcon(QIcon(pixmap))

        self.select_directory_button.clicked.connect(self._file_dialog)

    @classmethod
    def get_path(cls, parent):
        # TODO: Verify path is a real path

        dialog = cls(parent)
        result = dialog.exec_()

        if not result:
            return

        return Path(dialog.path_value.text())

    def _file_dialog(self):
        path = QFileDialog().getExistingDirectory(
            self,
            self.tr("Select directory containing identities"),
            QStandardPaths.writableLocation(QStandardPaths.HomeLocation),
            QFileDialog.ShowDirsOnly)

        self.path_value.setText(path)
