from typing import Optional

from PyQt5.QtWidgets import QWidget
from brainframe.api import bf_codecs

from .stream_widget_overlay_ui import StreamWidgetOverlayUI


class StreamWidgetOverlay(StreamWidgetOverlayUI):
    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)

    def change_stream(self,
                      stream_conf: Optional[bf_codecs.StreamConfiguration]) \
            -> None:

        if stream_conf is None:
            self.titlebar.set_stream_name(None)
        else:
            self.titlebar.set_stream_name(stream_conf.name)

    #     self._init_signals()
    #
    # def _init_signals(self) -> None:
    #     self.lagging_stream_indicator.clicked.connect(
    #         lambda: BrainFrameMessage)
    #     self.broken_stream_indicator.clicked.connect(lambda: print("B"))
    #
    # def handle_frame_metadata(self, frame_metadata: ZoneStatusFrameMeta) \
    #         -> None:
    #     self.lagging_stream_indicator.setVisible(
    #         frame_metadata.client_buffer_full)
    #     self.broken_stream_indicator.setVisible(frame_metadata.stream_broken)
