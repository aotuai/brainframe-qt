from typing import Optional

from PyQt5.QtWidgets import QWidget

from brainframe.client.ui.main_window.main_window_ui import MainWindowUI


class MainWindow(MainWindowUI):

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
