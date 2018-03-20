from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi


class MainWindow(QWidget):
    """Main window for entire UI

    This is a Widget plugin the event that it needs to handle slots and signals
    for its layouts. It might be squashed into ui.main in the future"""

    def __init__(self, parent=None):
        super().__init__(parent)

        loadUi("ui/main_window/main_window.ui", self)
