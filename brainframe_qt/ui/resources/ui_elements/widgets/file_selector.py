from pathlib import Path

from PyQt5.QtCore import QStandardPaths, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton, \
    QSizePolicy, \
    QWidget


class _FileSelectorUI(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.filepath_line_edit = self._init_filepath_line_edit()
        self.select_file_button = self._init_select_file_button()

        self._init_layout()
        self._init_style()

    def _init_filepath_line_edit(self) -> QLineEdit:
        filepath_line_edit = QLineEdit(self)

        return filepath_line_edit

    def _init_select_file_button(self) -> QPushButton:
        select_file_button = QPushButton(self)

        select_file_button.setIcon(QIcon(":/icons/folder"))

        return select_file_button

    def _init_layout(self) -> None:
        layout = QHBoxLayout()

        layout.addWidget(self.filepath_line_edit)
        layout.addWidget(self.select_file_button)

        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def _init_style(self) -> None:
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.filepath_line_edit.setSizePolicy(QSizePolicy.MinimumExpanding,
                                              QSizePolicy.Fixed)
        self.select_file_button.setSizePolicy(QSizePolicy.Fixed,
                                              QSizePolicy.Fixed)


class FileSelector(_FileSelectorUI):

    path_changed = pyqtSignal(Path)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_signals()

    def _init_signals(self) -> None:
        self.select_file_button.clicked.connect(self._get_filepath_dialog)

        self.filepath_line_edit.textChanged.connect(
            lambda filepath: self.path_changed.emit(Path(filepath)))

    @property
    def filepath(self) -> str:
        return self.filepath_line_edit.text()

    @filepath.setter
    def filepath(self, filepath: str) -> None:
        self.filepath_line_edit.setText(filepath)
        self.path_changed.emit(Path(filepath))

    def _get_filepath_dialog(self) -> None:
        # Second return value is ignored. PyQt5 returns what appears to be a
        # filter as a string as well, differing from the C++ implementation
        file_path, _ = QFileDialog().getOpenFileName(
            self,
            self.tr("Select video file"),
            QStandardPaths.writableLocation(QStandardPaths.HomeLocation))

        self.filepath = file_path
