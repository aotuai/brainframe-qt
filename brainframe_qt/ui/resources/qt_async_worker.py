import os
from typing import Callable

from PyQt5.QtCore import Qt, QThread, pyqtSlot
from PyQt5.QtWidgets import QWidget


class QTAsyncWorker(QThread):

    def __init__(self,
                 parent: QWidget,
                 func: Callable, callback: Callable,
                 *args, **kwargs):
        super().__init__(parent=parent)

        self.func = func
        self.callback = callback

        self.args = args
        self.kwargs = kwargs

        self.result = None
        self._terminated = False

        # Connect the parent's destructor signal
        # noinspection PyUnresolvedReferences
        self.parent().destroyed.connect(
            self._terminate,
            type=Qt.DirectConnection)

        # noinspection PyUnresolvedReferences
        self.finished.connect(self.finish)

    def run(self):
        self.result = self.func(*self.args, **self.kwargs)

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
            self.callback(self.result)
        self.deleteLater()

    @pyqtSlot()
    def _terminate(self):
        self._terminated = True
        self.wait()
