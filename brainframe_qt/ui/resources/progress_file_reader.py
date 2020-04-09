from pathlib import Path

from PyQt5.QtWidgets import QProgressDialog


class CancelledError(Exception):
    """Raised when the ProgressFileReader receives a cancel request from the
    QProgressDialog.
    """


_BLOCK_SIZE = 8192
"""A somewhat arbitrarily chosen upload block size."""


class ProgressFileReader:
    """An iterable that wraps around a file. When it is iterated, it reads
    bytes from the file and updates the given QProgressDialog. It raises a
    CancelledError to the iterating code when the user presses Cancel in the
    QProgressDialog.
    """

    def __init__(self, filepath: Path, progress_dialog: QProgressDialog):
        """
        :param filepath: The path to read file data from
        :param progress_dialog: The dialog to update on progress
        """
        self.filepath: Path = filepath
        self._file = None
        self._progress_dialog = progress_dialog

        self._progress_dialog.setMinimum(0)
        self._progress_dialog.setMaximum(filepath.stat().st_size)

        self._read_bytes = 0

    def __enter__(self):
        self._file = self.filepath.open("rb")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file is not None:
            self._file.close()

    def __iter__(self):
        while True:
            if self._progress_dialog.wasCanceled():
                raise CancelledError()

            data = self._file.read(_BLOCK_SIZE)
            if not data:
                break
            self._read_bytes += len(data)
            self._progress_dialog.setValue(self._read_bytes)
            yield data

    def __len__(self):
        return self.filepath.stat().st_size
