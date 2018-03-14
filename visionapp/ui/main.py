from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi


class Main(QMainWindow):
    """Main window for entire UI"""

    def __init__(self, parent=None):
        super().__init__(parent)

        loadUi("ui/main.ui", self).show()
