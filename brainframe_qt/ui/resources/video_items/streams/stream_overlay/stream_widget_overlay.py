from PyQt5.QtWidgets import QWidget

from .stream_widget_overlay_ui import StreamWidgetOverlayUI


class StreamWidgetOverlay(StreamWidgetOverlayUI):
    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)

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
