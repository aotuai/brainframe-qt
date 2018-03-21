from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from api import api

from ui.resources import client_paths
from .video_small.video_small import VideoSmall
from ui.resources.flow_layout import FlowLayout


class VideoThumbnailView(QWidget):

    thumbnail_stream_clicked_signal = pyqtSignal(int)
    """Used to alert outer widget of change"""

    remove_selection_border_signal = pyqtSignal(int)

    def __init__(self, parent=None):

        # TODO: Debug
        if api is not None:
            api.get_stream_configurations = \
                get_stream_configurations_debug

        super().__init__(parent)

        loadUi(client_paths.video_thumbnail_view_ui, self)

        self.layout_ = FlowLayout(self)
        self.setLayout(self.layout_)

        self.streams = {}
        if api is not None:
            for stream_conf in api.get_stream_configurations():
                video = VideoSmall(self, stream_conf, 30)
                self.streams[stream_conf.id_] = video
                self.layout_.addWidget(video)
        else:
            # Create fake videos for QtDesigner
            # TODO: Use mock for this
            for stream_conf in get_stream_configurations_debug():
                video = VideoSmall(self, stream_conf, 30)
                self.streams[stream_conf.id_] = video
                self.layout_.addWidget(video)

        self.current_stream_id = None

    @pyqtSlot(int)
    def thumbnail_stream_clicked_slot(self, stream_id):
        """Signaled by child VideoWidget and then passed upwards

        Also removes selection border from previously selected video"""
        print(f"Stream {stream_id} clicked")

        # TODO: Don't do anything if stream already active
        # if self.current_stream_id == stream_id:
        #     return

        # Remove selection border from previously selected video
        if self.current_stream_id:
            self.remove_selection_border_signal.emit(self.current_stream_id)

        # Alert outer widget
        self.thumbnail_stream_clicked_signal.emit(stream_id)

        # Store stream as current stream
        self.current_stream_id = stream_id

    @pyqtSlot()
    def remove_all_thumbnail_highlight_slots(self):
        """Called by outer widget when expanded video is explicitly closed

        Removes selection border from currently selected video
        """

        if self.current_stream_id:
            self.remove_selection_border_signal.emit(self.current_stream_id)
            self.current_stream_id = None


# DEBUG
def get_stream_configurations_debug():
    from api.data_structures import StreamConfiguration
    configs = [
        StreamConfiguration(name="Image1",
                            connection_type="image",
                            parameters={"path": "ui/resources/images/cat.jpg"},
                            id_=1010101),
        StreamConfiguration(name="Image1",
                            connection_type="image",
                            parameters={"path": "ui/resources/images/video.jpeg"},
                            id_=2020202)]

    return configs