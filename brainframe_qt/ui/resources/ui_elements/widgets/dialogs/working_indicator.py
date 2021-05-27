from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QKeyEvent, QCloseEvent
from PyQt5.QtWidgets import QProgressDialog


class WorkingIndicator(QProgressDialog):
    """Spinning progress bar that indicates work is being performed

    # https://www.qtcentre.org/threads/21414-Busy-Indicator-using-QProgressDialog?p=202257#post202257
    """

    def __init__(self, cancelable: bool = False, *, parent: QObject):
        super().__init__(parent=parent)

        self.cancelable = cancelable

        self._init_style()

    def _init_style(self):
        self.setModal(True)

        # Animated spinner progress bar instead of loading bar
        self.setRange(0, 0)

        if not self.cancelable:
            self.setCancelButton(None)

            # Remove close button if not cancelable (as far as WM supports)
            self.setWindowFlag(Qt.CustomizeWindowHint, True)
            self.setWindowFlag(Qt.WindowCloseButtonHint, False)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Disable the Esc key if not cancelable"""
        if event.key() is Qt.Key_Escape and not self.cancelable:
            event.ignore()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Disable Alt+F4 (or equivalent) if not cancelable"""
        # If we receive a closeEvent that is spontaneous, that means the event
        # originated outside of Qt (e.g. from the window manager)
        if event.spontaneous() and not self.cancelable:
            event.ignore()
        else:
            super().closeEvent(event)
