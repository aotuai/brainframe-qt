from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi

from visionapp.client.ui.resources.paths import qt_ui_paths


class MainWindow(QMainWindow):
    """Main window for entire UI

    This is a Widget plugin in the event that it needs to handle slots and
    signals for its layouts. It might be squashed into ui.main in the future
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        loadUi(qt_ui_paths.main_window_ui, self).show()

    @pyqtSlot()
    def show_video_expanded_view(self):
        """Called by thumbnail_view when a thumbnail is clicked"""
        self.video_layout.setStretch(0, 2)
        self.video_layout.setStretch(1, 5)

    @pyqtSlot()
    def hide_video_expanded_view(self):
        """Called by expanded_view when expanded video is closed"""
        self.video_layout.setStretch(0, 2)
        self.video_layout.setStretch(1, 0)

