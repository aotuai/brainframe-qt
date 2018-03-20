from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

import client_paths


class MainWindow(QWidget):
    """Main window for entire UI

    This is a Widget plugin the event that it needs to handle slots and signals
    for its layouts. It might be squashed into ui.main in the future"""

    def __init__(self, parent=None):
        super().__init__(parent)

        loadUi(client_paths.main_window_ui, self)
