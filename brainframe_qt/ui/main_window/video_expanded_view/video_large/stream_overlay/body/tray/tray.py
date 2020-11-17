from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSizePolicy, QVBoxLayout, QWidget

from .stream_alert import StreamAlert


class OverlayTray(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)

        self.lagging_stream_indicator = self._init_lagging_stream_indicator()

        self._init_layout()
        self._init_style()

    def _init_lagging_stream_indicator(self) -> StreamAlert:
        short_text = QApplication.translate("StreamWidgetOverlay",
                                            "Desynced analysis")

        message_text1 = QApplication.translate(
            "StreamWidgetOverlay",
            "The server is not processing frames quickly enough.")
        message_text2 = QApplication.translate(
            "StreamWidgetOverlay",
            "Results will not appear synced with the frames they correspond "
            + "to.")
        message_text = f"{message_text1}<br>{message_text2}"

        icon = QIcon(":/icons/analysis_error")

        lagging_stream_indicator = StreamAlert(icon, short_text, message_text,
                                               parent=self)

        return lagging_stream_indicator

    def _init_layout(self) -> None:
        layout = QVBoxLayout()

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.lagging_stream_indicator.setSizePolicy(QSizePolicy.Fixed,
                                                    QSizePolicy.Fixed)

        # Hide until needed
        self.lagging_stream_indicator.setHidden(True)

    def set_lagging(self, lagging: bool) -> None:
        self._display_alert_button(lagging, self.lagging_stream_indicator)

    def _display_alert_button(self, display: bool, button: StreamAlert) \
            -> None:
        if display:
            self.layout().addWidget(button)
        else:
            self.layout().removeWidget(button)

        button.setVisible(display)
