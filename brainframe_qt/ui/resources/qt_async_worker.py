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

    def run(self):
        self.result = self.func(*self.args, **self.kwargs)
