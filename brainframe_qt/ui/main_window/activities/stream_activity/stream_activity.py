from PyQt5.QtWidgets import QWidget

from brainframe.client.ui.main_window.activities.stream_activity.stream_activity_ui import \
    _StreamActivityUI
from brainframe.client.ui.resources.mixins.display import ExpandableMI


class StreamActivity(_StreamActivityUI, ExpandableMI):
    """This widget holds the thumbnail and expanded video views"""

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_signals()

    def _init_signals(self):
        self.video_thumbnail_view.thumbnail_stream_clicked_signal.connect(
            lambda: self.set_expanded(True))
        self.video_thumbnail_view.thumbnail_stream_clicked_signal.connect(
            self.video_expanded_view.open_expanded_view_slot)

        self.video_expanded_view.expanded_stream_closed_signal.connect(
            lambda: self.set_expanded(False))

        self.video_expanded_view.stream_delete_signal.connect(
            lambda: self.set_expanded(False))

    def expand(self, expanding: bool):
        self.video_expanded_view.setVisible(expanding)

        if not expanding:
            self.video_thumbnail_view.expand_thumbnail_layouts_slot()
