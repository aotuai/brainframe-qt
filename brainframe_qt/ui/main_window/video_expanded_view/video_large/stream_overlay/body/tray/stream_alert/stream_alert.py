from datetime import datetime, timedelta

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from brainframe.client.ui.main_window.video_expanded_view.video_large.stream_overlay import \
    AbstractOverlayAlert
from brainframe.client.ui.resources.ui_elements.buttons import IconButton
from brainframe.client.ui.resources.ui_elements.widgets.dialogs import \
    BrainFrameMessage


class StreamAlert(QWidget):
    ALERT_TIMEOUT = timedelta(seconds=10)
    """How long an inactive alert appears on screen before it is removed.
    This gives the alert time to reappear without causing a jittering affect"""

    def __init__(self, alert: AbstractOverlayAlert, *, parent: QWidget):
        super().__init__(parent=parent)

        self.alert = alert

        self._timeout = datetime.fromtimestamp(0)
        self.refresh_timeout()

        self.icon_button = self._init_icon_button()
        self.label = self._init_label()

        self._init_layout()
        self._init_style()

    def _init_icon_button(self) -> "_StreamAlertButton":
        icon_button = _StreamAlertButton(
            button_icon=self.alert.icon(),
            message_text=self.alert.long_text(),
            short_text=self.alert.short_text(),
            parent=self
        )
        return icon_button

    def _init_label(self) -> QLabel:
        label = QLabel(self.alert.short_text(), parent=self)

        return label

    def _init_layout(self) -> None:
        layout = QHBoxLayout()

        layout.addWidget(self.icon_button)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setToolTip(self.alert.long_text())

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    @property
    def past_minimum_duration(self) -> bool:
        return datetime.now() > self._timeout

    def refresh_timeout(self) -> None:
        self._timeout = datetime.now() + self.ALERT_TIMEOUT


class _StreamAlertButton(IconButton):
    def __init__(self, button_icon: QIcon, message_text: str, short_text: str,
                 *, parent: QWidget):
        super().__init__(button_icon, "", parent)

        message = BrainFrameMessage.information(
            parent=self,
            title=short_text,
            message=message_text
        )

        self.clicked.connect(message.show)
