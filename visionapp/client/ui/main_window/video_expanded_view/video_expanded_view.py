from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QWidget
from PyQt5.uic import loadUi

import client_paths
from .video_large.video_large import VideoLarge


class VideoExpandedView(QWidget):
    """Holds the expanded video view. Hidden when no stream selected"""

    expanded_stream_closed_signal = pyqtSignal()
    """Signaled when expanded stream is closed"""

    def __init__(self, parent):
        super().__init__(parent)

        loadUi(client_paths.video_expanded_view_ui, self)
        self.video_layout.addWidget(VideoLarge(self, 5))

        self.sizePolicy().setHorizontalStretch(0)

    @pyqtSlot(int)
    def open_expanded_view_slot(self, stream_id):
        """Signaled by thumbnail view when thumbnail video is clicked"""

        # self.expanded_video.change_stream(stream_id)
        # self.expanded_video.setHidden(False)
        # self.alert_log.setHidden(False)

        self.sizePolicy().setHorizontalStretch(5)
        print("Event")

        # Create new VideoLarge()
        # Create new AlertLog()
        # Adjust layout width

    @pyqtSlot()
    def expanded_stream_closed_slot(self):
        """Signaled by expanded video widget when widget is closed"""

        # self.expanded_video.change_stream(None)

        # self.expanded_video.setHidden(True)
        # self.alert_log.setHidden(False)

        # Alert slots that expanded stream was closed
        # VideoThumbnailView will remove highlight from thumbnail video
        self.expanded_stream_closed_signal.emit()
