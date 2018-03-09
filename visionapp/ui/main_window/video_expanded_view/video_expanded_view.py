from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi


class VideoExpandedView(QWidget):

    def __init__(self, parent):

        super().__init__(parent)

        loadUi("ui/main_window/video_expanded_view/video_expanded_view.ui")
