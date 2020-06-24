from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QProgressDialog


class WorkingIndicator(QProgressDialog):
    """Spinning progress bar that indicates work is being performed

    # https://www.qtcentre.org/threads/21414-Busy-Indicator-using-QProgressDialog?p=202257#post202257
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowModality(Qt.WindowModal)
        # https://forum.qt.io/post/423015
        self.setWindowFlags(Qt.Window
                            | Qt.WindowTitleHint
                            | Qt.CustomizeWindowHint)

        self.setCancelButton(None)
        self.setRange(0, 0)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Disable the Esc key"""
        if event.key() is Qt.Key_Escape:
            event.ignore()
