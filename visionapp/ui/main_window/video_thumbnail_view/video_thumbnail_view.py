from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi


class VideoThumbnailView(QWidget):

    def __init__(self, parent):

        super().__init__(parent)

        loadUi("ui/main_window/video_thumbnail_view/video_thumbnail_view.ui",
               self)
