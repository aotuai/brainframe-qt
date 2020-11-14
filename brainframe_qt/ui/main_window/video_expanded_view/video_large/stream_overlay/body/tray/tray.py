from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSizePolicy, QVBoxLayout, QWidget

from .stream_alert import StreamAlert


class OverlayTray(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)

        self.no_analysis_indicator = self._init_no_analysis_indicator()
        self.desynced_analysis_indicator \
            = self._init_desynced_analysis_indicator()
        self.buffer_full_indicator = self._init_buffer_full_indicator()

        self._init_layout()
        self._init_style()

    def _init_no_analysis_indicator(self) -> StreamAlert:
        short_text = QApplication.translate("StreamWidgetOverlay",
                                            "Awaiting analysis")

        message = QApplication.translate(
            "StreamWidgetOverlay",
            "No analysis results have been received for this stream yet")

        icon = QIcon(":/icons/analysis_error")

        lagging_stream_indicator = StreamAlert(icon, short_text, message,
                                               parent=self)

        return lagging_stream_indicator

    def _init_desynced_analysis_indicator(self) -> StreamAlert:
        short_text = QApplication.translate("StreamWidgetOverlay",
                                            "Desynced analysis")

        message_text1 = QApplication.translate(
            "StreamWidgetOverlay",
            "The server is not processing frames quickly enough.")
        message_text2 = QApplication.translate(
            "StreamWidgetOverlay",
            "Low analysis FPS will cause detections to appear before their "
            + "frames.")
        message_text = f"{message_text1}<br>{message_text2}"

        icon = QIcon(":/icons/analysis_error")

        lagging_stream_indicator = StreamAlert(icon, short_text, message_text,
                                               parent=self)

        return lagging_stream_indicator

    def _init_buffer_full_indicator(self) -> StreamAlert:
        short_text = QApplication.translate("StreamWidgetOverlay",
                                            "Severely desynced analysis")

        message_text1 = QApplication.translate(
            "StreamWidgetOverlay",
            "The server is processing frames extremely slowly.")
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

        self.no_analysis_indicator.setSizePolicy(QSizePolicy.Fixed,
                                                 QSizePolicy.Fixed)
        self.desynced_analysis_indicator.setSizePolicy(QSizePolicy.Fixed,
                                                       QSizePolicy.Fixed)
        self.buffer_full_indicator.setSizePolicy(QSizePolicy.Fixed,
                                                 QSizePolicy.Fixed)

        # Hide until needed
        self.no_analysis_indicator.setHidden(True)
        self.desynced_analysis_indicator.setHidden(True)
        self.buffer_full_indicator.setHidden(True)

    def set_no_analysis(self, no_analysis: bool) -> None:
        self._display_alert_button(no_analysis, self.no_analysis_indicator)

    def set_desynced_analysis(self, desynced_analysis: bool) -> None:
        self._display_alert_button(desynced_analysis,
                                   self.desynced_analysis_indicator)

    def set_buffer_full(self, buffer_full: bool) -> None:
        self._display_alert_button(buffer_full, self.buffer_full_indicator)

    def _display_alert_button(self, display: bool, button: StreamAlert) \
            -> None:
        if display:
            self.layout().addWidget(button)
        else:
            self.layout().removeWidget(button)

        button.setVisible(display)
