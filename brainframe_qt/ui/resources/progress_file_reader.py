from pathlib import Path
from typing import cast, Iterator
from io import BytesIO

from PyQt5.QtCore import QObject, pyqtSignal


class CanceledError(Exception):
    """Raised when the ProgressFileReader receives a cancel request from the
    QProgressDialog.
    """


# _BLOCK_SIZE = 8192
_BLOCK_SIZE = 8
"""A somewhat arbitrarily chosen upload block size."""


class ProgressFileReader(QObject):
    """An iterable that wraps around a file. When it is iterated, it reads
    bytes from the file and emits a signal reporting on the read progress.

    This can be used to update a UI on upload progress while making an API
    call.

    >>> reader = ProgressFileReader("/path/to/file")
    >>> # Connect process_signal to slots on a UI element
    >>> with reader:
    >>>     api.new_storage(reader, "application/octet-stream")
    """

    progress_signal = pyqtSignal(int)
    """Emitted when a chunk of data is read. Provides the total number of bytes
    read.
    """

    def __init__(self, filepath: Path, parent: QObject):
        """
        :param filepath: The path to read file data fro
        :param parent: The parent of this QObject
        """
        super().__init__(parent)
        self.filepath: Path = filepath
        self._file = cast(BytesIO, None)

        self._canceled = False
        self._total_read = 0

    @property
    def file_size(self) -> int:
        """
        :return: The total size of the file in bytes
        """
        return self.filepath.stat().st_size

    def cancel(self) -> None:
        """Stops reading prematurely by raising a CanceledError the next time
        this object is iterated.
        """
        self._canceled = True

    def __enter__(self) -> "ProgressFileReader":
        self._file = self.filepath.open("rb")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._file is not None:
            self._file.close()

    def __iter__(self) -> Iterator[bytes]:
        while True:
            data = self._file.read(_BLOCK_SIZE)
            if not data:
                break

            if self._canceled:
                raise CanceledError()
            self._total_read += len(data)
            self.progress_signal.emit(self._total_read)
            yield data

    def __len__(self) -> int:
        return self.filepath.stat().st_size
