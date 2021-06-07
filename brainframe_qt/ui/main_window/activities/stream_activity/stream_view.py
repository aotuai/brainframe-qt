from PyQt5.QtWidgets import QWidget
from brainframe.api import bf_codecs

from .stream_view_ui import _StreamViewUI


class StreamView(_StreamViewUI):
    """This widget holds the thumbnail and expanded video views"""

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_signals()

    def _init_signals(self):
        self.video_thumbnail_view.stream_clicked.connect(self.open_expanded_view)

        self.video_expanded_view.expanded_stream_closed_signal.connect(
            lambda: self.display_expanded_video(False))

        self.video_expanded_view.stream_delete_signal.connect(
            self.video_thumbnail_view.delete_stream_conf)
        self.video_expanded_view.stream_delete_signal.connect(
            lambda: self.display_expanded_video(False))

    def open_expanded_view(self, stream_conf: bf_codecs.StreamConfiguration):
        self.video_expanded_view.open_expanded_view_slot(stream_conf)
        self.display_expanded_video(True)

    def display_expanded_video(self, display: bool):
        self.video_expanded_view.setVisible(display)

        self.video_thumbnail_view.expand_video_grids(not display)
