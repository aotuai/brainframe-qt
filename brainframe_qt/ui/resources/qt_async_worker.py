import os

from PyQt5.QtCore import QThread


class QTAsyncWorker(QThread):

    def __init__(self, parent, func, callback, *args, **kwargs):
        super().__init__(parent=parent)

        self.func = func
        self.callback = callback

        self.args = args
        self.kwargs = kwargs

        self.result = None

        # noinspection PyUnresolvedReferences
        self.finished.connect(lambda: callback(self.result))

        # noinspection PyUnresolvedReferences
        self.finished.connect(self.deleteLater)

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
