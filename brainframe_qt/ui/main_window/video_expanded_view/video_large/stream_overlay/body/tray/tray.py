from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget

from brainframe.client.ui.resources.ui_elements.buttons import TextIconButton
from brainframe.client.ui.resources.ui_elements.widgets.dialogs import \
    BrainFrameMessage


class OverlayTray(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)

        self.lagging_stream_indicator = self._init_lagging_stream_indicator()
        self.broken_stream_indicator = self._init_broken_stream_indicator()

        self._init_layout()
        self._init_style()

    def _init_lagging_stream_indicator(self) -> "_StreamAlertButton":
        message_text1 = QApplication.translate(
            "StreamWidgetOverlay",
            "The server is not processing frames quickly enough.")
        message_text2 = QApplication.translate(
            "StreamWidgetOverlay",
            "Results will not appear synced with the frames they correspond "
            + "to.")

        title = QApplication.translate("StreamWidgetOverlay", "Lagging stream")

        message_text = f"{message_text1}<br>{message_text2}"
        lagging_stream_indicator = _StreamAlertButton("❗", message_text, title,
                                                      parent=self)

        return lagging_stream_indicator

    def _init_broken_stream_indicator(self) -> "_StreamAlertButton":
        message_text = QApplication.translate(
            "StreamWidgetOverlay",
            "This stream is having trouble communicating"
        )

        title = QApplication.translate(
            "StreamWidgetOverlay",
            "Stream is broken"
        )

        broken_stream_indicator = _StreamAlertButton("❗", message_text, title,
                                                     parent=self)

        return broken_stream_indicator

    def _init_layout(self) -> None:
        layout = QVBoxLayout()

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        # self.layout().setContentsMargins(0, 0, 0, 0)

    def set_lagging(self, lagging: bool) -> None:
        self._display_alert_button(lagging, self.lagging_stream_indicator)

    def set_broken(self, broken: bool) -> None:
        self._display_alert_button(broken, self.broken_stream_indicator)

    def _display_alert_button(self, display: bool,
                              button: "_StreamAlertButton") \
            -> None:
        if display:
            self.layout().addWidget(button)
        else:
            self.layout().removeWidget(button)

        button.setVisible(display)


class _StreamAlertButton(TextIconButton):
    def __init__(self, button_text: str, message_text: str, title: str, *,
                 parent: QWidget):
        super().__init__(button_text, parent)

        self.setToolTip(message_text)

        message = BrainFrameMessage.information(
            parent=self,
            title=title,
            message=message_text
        )

        self.clicked.connect(message.show)

        # Hide until needed
        self.setHidden(True)
