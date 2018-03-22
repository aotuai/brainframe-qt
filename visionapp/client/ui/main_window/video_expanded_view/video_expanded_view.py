from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QWidget
from PyQt5.uic import loadUi

from ui.resources import client_paths
from .video_large.video_large import VideoLarge


class VideoExpandedView(QWidget):
    """Holds the expanded video view. Hidden when no stream selected"""

    expanded_stream_closed_signal = pyqtSignal()
    """Signaled when expanded stream is closed"""

    def __init__(self, parent):
        super().__init__(parent)

        loadUi(client_paths.video_expanded_view_ui, self)

        self._set_widgets_hidden(True)

    @pyqtSlot(int)
    def open_expanded_view_slot(self, stream_id):
        """Signaled by thumbnail view when thumbnail video is clicked"""

        # TODO:
        # self.expanded_video.change_stream(stream_id)

        # Show expanded view widgets
        self._set_widgets_hidden(False)

        self.sizePolicy().setHorizontalStretch(5)

    @pyqtSlot()
    def expanded_stream_closed_slot(self):
        """Signaled by expanded video widget when widget is closed"""

        # TODO:
        # self.expanded_video.change_stream(None)

        # Hide expanded view widgets
        self._set_widgets_hidden(True)

        # Alert slots that expanded stream was closed
        # VideoThumbnailView will remove highlight from thumbnail video
        self.expanded_stream_closed_signal.emit()

    @pyqtSlot()
    def open_task_config(self):
        print("Opening task configuration")

    @pyqtSlot()
    def open_source_config(self):
        print("Opening source configuration")

    def _set_widgets_hidden(self, hidden=True):
        self.expanded_video.setHidden(hidden)
        self.hide_button.setHidden(hidden)
        self.alert_log.setHidden(hidden)
        self.task_config_button.setHidden(hidden)
        self.source_config_button.setHidden(hidden)