from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy, QFrame

from brainframe.client.api.codecs import Alert
from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.paths import qt_qss_paths


class AlertLogEntryUI(QFrame):

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)

        self.time_label = self._init_time_label()
        self.active_state_label = self._init_active_state_label()
        self.alert_description_label = self._init_alert_description_label()

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QHBoxLayout()

        layout.addWidget(self.time_label)
        layout.addWidget(self.active_state_label)
        layout.addWidget(self.alert_description_label)

        self.setLayout(layout)

    def _init_style(self):
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alert_log_entry_qss)

    def _init_time_label(self) -> QLabel:
        time_label = QLabel("13:37", self)
        time_label.setObjectName("time")

        time_label.setFixedWidth(self._text_width("22:22"))

        time_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        return time_label

    def _init_active_state_label(self) -> QLabel:
        active_state_label = QLabel("Inactive", self)
        active_state_label.setObjectName("active_state")

        active_state_label.setFixedWidth(self._text_width("Inactive"))

        active_state_label.setSizePolicy(QSizePolicy.Preferred,
                                         QSizePolicy.Fixed)
        return active_state_label

    def _init_alert_description_label(self) -> QLabel:
        alert_description_label = QLabel("Tyler has smelly feet", self)
        alert_description_label.setObjectName("alert_description")
        alert_description_label.setSizePolicy(QSizePolicy.Expanding,
                                              QSizePolicy.Maximum)
        return alert_description_label

    def _text_width(self, string: str) -> int:
        return self.fontMetrics().boundingRect(string).width()


class AlertLogEntry(AlertLogEntryUI):

    def __init__(self, alert: Alert, parent: QWidget):
        super().__init__(parent)

