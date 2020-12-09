from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QWidget

from brainframe_qt.api_utils.streaming.zone_status_frame import \
    ZoneStatusFrame
from .stream_listener_widget import StreamListenerWidget
from .stream_widget_ui import StreamWidgetUI


class StreamWidget(StreamWidgetUI, StreamListenerWidget):
    """Base widget that uses Stream object to get frames.

    Makes use of a QTimer to get frames
    """

    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)

    def resizeEvent(self, _event: Optional[QResizeEvent] = None) -> None:
        """Take up entire width using aspect ratio of scene"""

        current_frame = self.scene().current_frame

        if current_frame is not None:
            # EXTREMELY IMPORTANT LINE!
            # The sceneRect grows but never shrinks automatically
            self.scene().setSceneRect(current_frame.boundingRect())
            self.fitInView(current_frame.boundingRect(), Qt.KeepAspectRatio)

    def on_frame(self, frame: ZoneStatusFrame) -> None:

        self.scene().remove_all_items()
        self.scene().set_frame(frame=frame.frame)

        # This frame has never been paired with ZoneStatuses from the server
        # so nothing should be rendered. This occurs when the server has
        # never ever returned results for this stream. This could happen if the
        # server was unable to connect to the stream, or inference crashed
        # immediately on the first frame of processing
        if frame.zone_statuses is None:
            return

        if self.render_config.draw_lines:
            self.scene().draw_lines(frame.zone_statuses)

        if self.render_config.draw_regions:
            self.scene().draw_regions(frame.zone_statuses)

        if self.render_config.draw_detections:
            self.scene().draw_detections(
                frame_tstamp=frame.tstamp,
                tracks=frame.tracks
            )

    def on_stream_init(self) -> None:
        self.scene().remove_all_items()
        self.scene().set_frame(path=":/images/connecting_to_stream_png")

    def on_stream_halted(self) -> None:
        self.scene().remove_all_items()
        self.scene().set_frame(path=":/images/connection_lost_png")

    def on_stream_closed(self) -> None:
        self.on_stream_halted()

    def on_stream_error(self) -> None:
        self.scene().remove_all_items()
        self.scene().set_frame(path=":/images/error_message_png")
