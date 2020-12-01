from typing import Optional

from PyQt5.QtWidgets import QSizePolicy, QVBoxLayout, QWidget
from brainframe.api import bf_codecs

from brainframe_qt.api_utils.streaming.zone_status_frame import \
    ZoneStatusFrame
from brainframe_qt.ui.resources.video_items.streams import StreamWidget
from .stream_overlay import StreamWidgetOverlay


class VideoLarge(StreamWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)

        self.stream_overlay = self._init_stream_overlay()

        self._init_layout()
        self._init_style()

    def _init_stream_overlay(self) -> StreamWidgetOverlay:
        stream_overlay = StreamWidgetOverlay(parent=self)

        return stream_overlay

    def _init_layout(self) -> None:
        layout = QVBoxLayout()

        layout.addWidget(self.stream_overlay)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def _init_style(self):
        # I was under the impression that this was the default size policy, but
        # removing it prevents the alert log from expanding into more than half
        # of the layout when the VideoLarge widget is very narrow
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def change_stream(self,
                      stream_conf: Optional[bf_codecs.StreamConfiguration]) \
            -> None:

        super().change_stream(stream_conf)

        self.stream_overlay.change_stream(stream_conf)

    def on_frame(self, frame: ZoneStatusFrame):
        super().on_frame(frame)
        self.stream_overlay.handle_frame_metadata(frame.frame_metadata)
