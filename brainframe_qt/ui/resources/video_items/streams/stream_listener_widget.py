from typing import Optional

from PyQt5.QtWidgets import QWidget

from brainframe.api.bf_codecs import StreamConfiguration
from brainframe.api.bf_errors import StreamConfigNotFoundError, StreamNotOpenedError
from gstly.abstract_stream_reader import StreamStatus

from brainframe_qt.api_utils import api, get_stream_manager
from brainframe_qt.api_utils.streaming import StreamListener, SyncedStreamReader
from brainframe_qt.api_utils.streaming.zone_status_frame import ZoneStatusFrame
from brainframe_qt.ui.resources import QTAsyncWorker


class StreamListenerWidget(QWidget, StreamListener):

    def __init__(self, *, parent: QWidget):
        QWidget.__init__(self, parent=parent)
        StreamListener.__init__(self)

        self.stream_conf: Optional[StreamConfiguration] = None
        """Current stream configuration used by the StreamReader"""

        self.stream_reader: Optional[SyncedStreamReader] = None

    def on_frame(self, frame: ZoneStatusFrame) -> None:
        pass

    def on_stream_init(self) -> None:
        pass

    def on_stream_closed(self) -> None:
        pass

    def on_stream_error(self) -> None:
        pass

    def on_stream_halted(self) -> None:
        pass

    def change_stream(self, stream_conf: Optional[StreamConfiguration]) -> None:

        self.stream_conf = stream_conf

        if not stream_conf:
            self._disconnect_stream_reader()
            self.stream_reader = None
            return

        def handle_stream_url(stream_url: Optional[str]) -> None:
            # Occurs when the get_stream_url() call fails due to
            # the stream having been deleted
            if stream_url is None:
                return

            # User must have already changed stream again by the time this callback is
            # called. Just forget about this current change request.
            if stream_conf is not self.stream_conf:
                return

            self._subscribe_to_stream(stream_conf, stream_url)

        QTAsyncWorker(self, self._get_stream_url, f_args=(stream_conf,),
                      on_success=handle_stream_url) \
            .start()

    def _disconnect_stream_reader(self) -> None:
        # Disconnect existing signals
        # This will be unnecessary when composition is used with StreamListener instead
        # of inheritance and PyQt manages this during GC.
        if self.stream_reader is not None:
            self.stream_reader.frame_received.disconnect(self.on_frame)
            self.stream_reader.stream_state_changed.disconnect(self._on_state_change)

    def _on_state_change(self, state: StreamStatus) -> None:
        if state is StreamStatus.INITIALIZING:
            self.on_stream_init()
        elif state is StreamStatus.HALTED:
            self.on_stream_halted()
        elif state is StreamStatus.CLOSED:
            self.on_stream_closed()
        elif state is StreamStatus.STREAMING:
            # Streaming, but no frame received yet
            self.on_stream_init()
        else:
            self.on_stream_error()

    def _subscribe_to_stream(
        self,
        stream_conf: StreamConfiguration,
        stream_url: str
    ) -> None:

        # Create the stream reader
        stream_manager = get_stream_manager()
        stream_reader = stream_manager.start_streaming(stream_conf, stream_url)

        if stream_reader is None:
            # This will happen if we try to get a StreamReader for a stream that no
            # longer exists, for example if a user clicks to expand a stream the very
            # instant before it's deleted from the server. We don't want to do anything
            return

        self._disconnect_stream_reader()

        # Connect new signals
        stream_reader.frame_received.connect(self.on_frame)
        stream_reader.stream_state_changed.connect(self._on_state_change)

        self.stream_reader = stream_reader

        # Don't wait for the first event to start displaying
        latest_frame = self.stream_reader.latest_processed_frame
        if latest_frame is not None:
            self.on_frame(latest_frame)
        else:
            self._on_state_change(stream_reader.status)

    @staticmethod
    def _get_stream_url(stream_conf: StreamConfiguration) -> Optional[str]:
        try:
            return api.get_stream_url(stream_conf.id)
        except (StreamConfigNotFoundError, StreamNotOpenedError):
            return None
