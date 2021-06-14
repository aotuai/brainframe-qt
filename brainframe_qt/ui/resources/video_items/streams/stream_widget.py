from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QWidget
from brainframe.api.bf_codecs import StreamConfiguration

from brainframe_qt.api_utils.streaming.zone_status_frame import ZoneStatusFrame
from .stream_listener_widget import StreamEventManager
from .stream_widget_ui import StreamWidgetUI


class StreamWidget(StreamWidgetUI):
    """Base widget that uses Stream object to get frames.

    Makes use of a QTimer to get frames
    """

    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)

        self.stream_manager = StreamEventManager(parent=self)

        self._draw_lines: Optional[bool] = None
        self._draw_regions: Optional[bool] = None
        self._draw_detections: Optional[bool] = None

        self.__init_signals()

    def __init_signals(self) -> None:
        self.stream_manager.frame_received.connect(self.on_frame)

        self.stream_manager.stream_initializing.connect(self.on_stream_init)
        self.stream_manager.stream_halted.connect(self.on_stream_halted)
        self.stream_manager.stream_closed.connect(self.on_stream_halted)
        self.stream_manager.stream_error.connect(self.on_stream_error)

    def resizeEvent(self, _event: Optional[QResizeEvent] = None) -> None:
        """Take up entire width using aspect ratio of scene"""

        current_frame = self.scene().current_frame

        if current_frame is not None:
            # EXTREMELY IMPORTANT LINE!
            # The sceneRect grows but never shrinks automatically
            self.scene().setSceneRect(current_frame.boundingRect())
            self.fitInView(current_frame.boundingRect(), Qt.KeepAspectRatio)

    @property
    def draw_lines(self) -> bool:
        if self._draw_lines is None:
            return self.render_config.draw_lines
        else:
            return self._draw_lines

    @draw_lines.setter
    def draw_lines(self, draw_lines: bool):
        self._draw_lines = draw_lines

    @property
    def draw_regions(self) -> bool:
        if self._draw_regions is None:
            return self.render_config.draw_regions
        else:
            return self._draw_regions

    @draw_regions.setter
    def draw_regions(self, draw_regions: bool):
        self._draw_regions = draw_regions

    @property
    def draw_detections(self) -> bool:
        if self._draw_detections is None:
            return self.render_config.draw_detections
        else:
            return self._draw_detections

    @draw_detections.setter
    def draw_detections(self, draw_detections: bool):
        self._draw_detections = draw_detections

    def change_stream(self, stream_conf: Optional[StreamConfiguration]) -> None:
        if stream_conf is None:
            self.stream_manager.stop_streaming()
        else:
            self.stream_manager.change_stream(stream_conf)

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

        if self.draw_lines:
            self.scene().draw_lines(frame.zone_statuses)

        if self.draw_regions:
            self.scene().draw_regions(frame.zone_statuses)

        if self.draw_detections:
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

    def on_stream_error(self) -> None:
        self.scene().remove_all_items()
        self.scene().set_frame(path=":/images/error_message_png")
