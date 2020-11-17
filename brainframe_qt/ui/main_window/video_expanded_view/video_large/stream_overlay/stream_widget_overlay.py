from datetime import timedelta
from typing import List, Optional

from PyQt5.QtWidgets import QWidget
from brainframe.api import bf_codecs

from brainframe.client.api_utils.streaming.zone_status_frame import \
    ZoneStatusFrameMeta
from . import alerts as stream_alerts
from .stream_widget_overlay_ui import StreamWidgetOverlayUI


class StreamWidgetOverlay(StreamWidgetOverlayUI):
    MIN_DESYNC_LATENCY_ALERT = timedelta(seconds=1)

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

        alerts = self._metadata_to_alerts(frame_metadata)
        self.body.handle_alerts(alerts)

    def _metadata_to_alerts(self, frame_metadata: ZoneStatusFrameMeta) \
            -> List[stream_alerts.AbstractOverlayAlert]:
        alerts: List[stream_alerts.AbstractOverlayAlert] = []

        if frame_metadata.no_analysis:
            alerts.append(stream_alerts.NO_ANALYSIS_ALERT)
        if frame_metadata.analysis_latency > self.MIN_DESYNC_LATENCY_ALERT:
            alerts.append(stream_alerts.DESYNCED_ANALYSIS_ALERT)
        if frame_metadata.client_buffer_full:
            alerts.append(stream_alerts.BUFFER_FULL_ALERT)

        return alerts
