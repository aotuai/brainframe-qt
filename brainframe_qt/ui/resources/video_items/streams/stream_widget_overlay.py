from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget

from brainframe.client.api_utils.streaming.zone_status_frame import \
    ZoneStatusFrameMeta
from brainframe.client.ui.resources.ui_elements.buttons import TextIconButton
from brainframe.client.ui.resources.ui_elements.widgets.dialogs import \
    BrainFrameMessage


class StreamWidgetOverlay(QWidget):
    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)

        self.lagging_stream_indicator = self._init_lagging_stream_indicator()
        self.broken_stream_indicator = self._init_broken_stream_indicator()

        self._init_layout()
        self._init_style()

        self._init_signals()

    def _init_lagging_stream_indicator(self) -> TextIconButton:
        lagging_stream_indicator = TextIconButton("❗", self)

        message_text1 = QApplication.translate(
            "StreamWidgetOverlay",
            "The server is not processing frames quickly enough.")
        message_text2 = QApplication.translate(
            "StreamWidgetOverlay",
            "Results will not appear synced with the frames they correspond "
            + "to.")

        message_text = f"{message_text1}<br>{message_text2}"

        lagging_stream_indicator.setToolTip(message_text)

        message = BrainFrameMessage.information(
            parent=lagging_stream_indicator,
            title="Lagging stream",
            message=message_text
        )
        lagging_stream_indicator.clicked.connect(message.show)

        return lagging_stream_indicator

    def _init_broken_stream_indicator(self) -> TextIconButton:
        broken_stream_indicator = TextIconButton("❗", self)

        message_text = "This stream is having trouble communicating"

        broken_stream_indicator.setToolTip(message_text)

        message = BrainFrameMessage.information(
            parent=broken_stream_indicator,
            title="Stream is broken",
            message=message_text
        )

        broken_stream_indicator.clicked.connect(message.show)

        return broken_stream_indicator

    def _init_layout(self) -> None:
        layout = QVBoxLayout()

        layout.addWidget(self.lagging_stream_indicator)
        layout.addWidget(self.broken_stream_indicator)

        self.setLayout(layout)

    def _init_style(self):
        ...

    def _init_signals(self) -> None:
        self.lagging_stream_indicator.clicked.connect(
            lambda: BrainFrameMessage)
        self.broken_stream_indicator.clicked.connect(lambda: print("B"))

    def handle_frame_metadata(self, frame_metadata: ZoneStatusFrameMeta) \
            -> None:
        self.lagging_stream_indicator.setVisible(
            frame_metadata.client_buffer_full)
        self.broken_stream_indicator.setVisible(frame_metadata.stream_broken)
