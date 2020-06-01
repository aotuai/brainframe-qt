import typing
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressBar, QProgressDialog, QWidget


class FileUploadProgressDialog(QProgressDialog):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._filepath = typing.cast(Path, None)
        self.progress_bar = self._init_progress_bar()

        self._init_layout()
        self._init_style()

    def _init_progress_bar(self) -> QProgressBar:
        progress_bar = QProgressBar(self)

        progress_bar.setFormat("%v kB/%m kB (%p%)")
        progress_bar.setMinimum(0)

        return progress_bar

    def _init_layout(self) -> None:
        self.setBar(self.progress_bar)

    def _init_style(self) -> None:
        self.setWindowModality(Qt.WindowModal)

    @property
    def filepath(self) -> Path:
        return self._filepath

    @filepath.setter
    def filepath(self, filepath: Path) -> None:
        self._filepath = filepath
        self._update_label_text()
        self.setMaximum(filepath.stat().st_size / 1000)

    def _update_label_text(self) -> None:
        label_text = self.tr("Uploading {filepath}...") \
            .format(filepath=self.filepath)
        self.setLabelText(label_text)
