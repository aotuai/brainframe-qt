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

    @pyqtSlot(int)
    def open_expanded_view_slot(self, stream_id):
        """Signaled by thumbnail view when thumbnail video is clicked"""

        # TODO:
        # self.expanded_video.change_stream(stream_id)

        # TODO: Don't hardcode these
        self.expanded_video.setHidden(False)
        self.hide_button.setHidden(False)
        self.alert_log.setHidden(False)
        self.task_config_button.setHidden(False)
        self.source_config_button.setHidden(False)

        self.sizePolicy().setHorizontalStretch(5)

    @pyqtSlot()
    def expanded_stream_closed_slot(self):
        """Signaled by expanded video widget when widget is closed"""

        # TODO:
        # self.expanded_video.change_stream(None)

        # TODO: Don't hardcode these
        self.expanded_video.setHidden(True)
        self.hide_button.setHidden(True)
        self.alert_log.setHidden(True)
        self.task_config_button.setHidden(True)
        self.source_config_button.setHidden(True)

        # Alert slots that expanded stream was closed
        # VideoThumbnailView will remove highlight from thumbnail video
        self.expanded_stream_closed_signal.emit()

    @pyqtSlot()
    def open_task_config(self):
        print("Opening task configuration")

    @pyqtSlot()
    def open_source_config(self):
        print("Opening source configuration")