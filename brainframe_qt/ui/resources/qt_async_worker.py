import os
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar
from threading import Event

from PyQt5.QtCore import Qt, QThread, pyqtSlot, QObject


class QTAsyncWorker(QThread):

    CallbackT = TypeVar('CallbackT')

    def __init__(self,
                 parent: QObject,
                 func: Callable[..., CallbackT], *,
                 f_args: Tuple = None, f_kwargs: Dict = None,
                 on_success: Optional[Callable[[CallbackT], Any]] = None,
                 on_error: Optional[Callable[[CallbackT], Any]] = None):
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
        super().start(*args, **kwargs)

    def finish(self):
        if not self._terminated:
            self.finished_event.set()

            if self.err:
                if self.on_error is not None:
                    self.on_error(self.err)
                else:
                    raise self.err
            elif self.on_success is not None:
                self.on_success(self.data)

        self.deleteLater()

    @pyqtSlot()
    def _terminate(self):
        self._terminated = True
        self.wait()
