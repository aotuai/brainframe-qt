import os
from typing import Callable, Dict, Optional, Tuple, TypeVar
from threading import Event

from PyQt5.QtCore import Qt, QThread, pyqtSlot
from PyQt5.QtWidgets import QWidget


class QTAsyncWorker(QThread):

    CallbackT = TypeVar('CallbackT')

    def __init__(self,
                 parent: QWidget,
                 func: Callable[..., CallbackT], *,
                 f_args: Tuple = None, f_kwargs: Dict = None,
                 on_success: Optional[Callable[[CallbackT], None]] = None,
                 on_error: Optional[Callable[[CallbackT], None]] = None):
        super().__init__(parent=parent)

        self.func = func
        self.on_success = on_success
        self.on_error = on_error

        self.f_args = f_args or ()
        self.f_kwargs = f_kwargs or {}

        self.err = None
        self.data = None
        self._terminated = False

        # Connect the parent's destructor signal
        # noinspection PyUnresolvedReferences
        self.parent().destroyed.connect(
            self._terminate,
            type=Qt.DirectConnection)

        # noinspection PyUnresolvedReferences
        self.finished.connect(self.finish)

        self.finished_event = Event()
        """An event that is set when the worker has finished, but before the 
        callback is run.
        """

    def run(self):
        try:
            self.data = self.func(*self.f_args, **self.f_kwargs)
        except Exception as exc:
            self.err = exc
            self.data = None

    def start(self, *args, **kwargs):
        # We don't want to use threads when using QtDesigner. If a plugin's
        # __init__ contains a QThread that is not complete by the time the
        # __init__ method finishes, it will crash
        # This environment variable is only set when running QtDesigner
        if os.getenv("PYQTDESIGNERPATH") is not None:
            self.run()
            # noinspection PyUnresolvedReferences
            self.finished.emit()
        else:
            super().start(*args, **kwargs)

    def finish(self):
        if not self._terminated:
            self.finished_event.set()

            if self.err and self.on_error is not None:
                self.on_error(self.err)
            elif self.on_success is not None:
                self.on_success(self.data)

        self.deleteLater()

    @pyqtSlot()
    def _terminate(self):
        self._terminated = True
        self.wait()
