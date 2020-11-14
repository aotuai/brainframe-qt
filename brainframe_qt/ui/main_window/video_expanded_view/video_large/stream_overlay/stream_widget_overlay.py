from typing import Optional

from PyQt5.QtWidgets import QWidget
from brainframe.api import bf_codecs

from brainframe.client.api_utils.streaming.zone_status_frame import \
    ZoneStatusFrameMeta
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

    def handle_frame_metadata(self, frame_metadata: ZoneStatusFrameMeta) \
            -> None:
        self.body.tray.set_no_analysis(frame_metadata.no_analysis)
        self.body.tray.set_desynced_analysis(
            frame_metadata.analysis_latency)
        self.body.tray.set_buffer_full(frame_metadata.client_buffer_full)
