from pathlib import Path
from typing import cast, Iterator
from io import BytesIO
from time import time

from PyQt5.QtCore import QObject, pyqtSignal


class CanceledError(Exception):
    """Raised when the ProgressFileReader receives a cancel request from the
    QProgressDialog.
    """


_BLOCK_SIZE = 1024000
"""The block size to read files at. Chosen from this answer:
https://stackoverflow.com/a/3673731
"""


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
    """Emitted when a chunk of data is read. Provides the total number of
    kilobytes read.
    """

    def __init__(self, filepath: Path, parent: QObject):
        """
        :param filepath: The path to read file data fro
        :param parent: The parent of this QObject
        """
        super().__init__(parent)
        self.filepath: Path = filepath
        self.file_size_kb = self.filepath.stat().st_size / 1000
        """The total size of the file in kilobytes"""
        self._file = cast(BytesIO, None)

        self._canceled = False

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
        total_read_kb = 0
        last_time_emitted = 0

        while True:
            if self._canceled:
                raise CanceledError()

            data = self._file.read(_BLOCK_SIZE)
            if not data:
                break
            total_read_kb += len(data) / 1000

            yield data

            # Emit progress 60 times per second and when the file is finished
            # being read. This limiter prevents the emit queue from being
            # filled up at small block sizes.
            emit_due = time() - last_time_emitted >= (1/60)
            finished = total_read_kb >= self.file_size_kb
            if emit_due or finished:
                self.progress_signal.emit(total_read_kb)
                last_time_emitted = time()

    def __len__(self) -> int:
        return self.filepath.stat().st_size
