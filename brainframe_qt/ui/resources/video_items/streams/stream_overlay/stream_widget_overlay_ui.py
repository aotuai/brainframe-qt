from PyQt5.QtWidgets import QVBoxLayout, QWidget

from .body import OverlayBody
from .titlebar import OverlayTitlebar


class StreamWidgetOverlayUI(QWidget):
    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)

        self.titlebar = self._init_titlebar()
        self.body = self._init_body()

        self._init_layout()
        self._init_style()

    def _init_titlebar(self) -> OverlayTitlebar:
        titlebar = OverlayTitlebar(parent=self)

        return titlebar

    def _init_body(self) -> OverlayBody:
        body = OverlayBody(parent=self)

        return body

    # def _init_lagging_stream_indicator(self) -> TextIconButton:
    #     lagging_stream_indicator = TextIconButton("❗", self)
    #
    #     message_text1 = QApplication.translate(
    #         "StreamWidgetOverlay",
    #         "The server is not processing frames quickly enough.")
    #     message_text2 = QApplication.translate(
    #         "StreamWidgetOverlay",
    #         "Results will not appear synced with the frames they correspond "
    #         + "to.")
    #
    #     message_text = f"{message_text1}<br>{message_text2}"
    #
    #     lagging_stream_indicator.setToolTip(message_text)
    #
    #     message = BrainFrameMessage.information(
    #         parent=lagging_stream_indicator,
    #         title="Lagging stream",
    #         message=message_text
    #     )
    #     lagging_stream_indicator.clicked.connect(message.show)
    #
    #     return lagging_stream_indicator
    #
    # def _init_broken_stream_indicator(self) -> TextIconButton:
    #     broken_stream_indicator = TextIconButton("❗", self)
    #
    #     message_text = "This stream is having trouble communicating"
    #
    #     broken_stream_indicator.setToolTip(message_text)
    #
    #     message = BrainFrameMessage.information(
    #         parent=broken_stream_indicator,
    #         title="Stream is broken",
    #         message=message_text
    #     )
    #
    #     broken_stream_indicator.clicked.connect(message.show)
    #
    #     return broken_stream_indicator

    def _init_layout(self) -> None:
        layout = QVBoxLayout()

        # layout.addWidget(self.lagging_stream_indicator)
        # layout.addWidget(self.broken_stream_indicator)

        layout.addWidget(self.titlebar)
        layout.addWidget(self.body)

        self.setLayout(layout)

    def _init_style(self):
        ...
