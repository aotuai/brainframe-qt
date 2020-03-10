import pendulum
from cached_property import cached_property

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QWidget

from brainframe.client.api.codecs import Alert
from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.mixins.mouse import ClickableMI
from brainframe.client.ui.resources.paths import qt_qss_paths


class AlertLogEntryUI(QFrame):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.start_time_label = self._init_start_time_label()
        self.time_dash_label = self._init_time_dash_label()
        self.end_time_label = self._init_end_time_label()
        # self.active_state_label = self._init_active_state_label()
        # self.alert_description_label = self._init_alert_description_label()

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QHBoxLayout()

        layout.addWidget(self.start_time_label)
        layout.addWidget(self.time_dash_label)
        layout.addWidget(self.end_time_label)
        layout.addStretch()
        # layout.addWidget(self.active_state_label)
        # layout.addWidget(self.alert_description_label)

        self.setLayout(layout)

    def _init_style(self):
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alert_log_entry_qss)

    def _init_start_time_label(self) -> QLabel:
        start_time_label = QLabel("00:00", self)
        start_time_label.setObjectName("start_time")

        start_time_label.setFixedWidth(self._max_time_width)

        start_time_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return start_time_label

    def _init_time_dash_label(self) -> QLabel:
        time_dash_label = QLabel("–", self)
        time_dash_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return time_dash_label

    def _init_end_time_label(self) -> QLabel:
        end_time_label = QLabel("00:00", self)
        end_time_label.setObjectName("end_time")

        end_time_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return end_time_label

    # def _init_active_state_label(self) -> QLabel:
    #     active_state_label = QLabel("[Alert Activeness]", self)
    #     active_state_label.setObjectName("active_state")
    #
    #     active_state_label.setFixedWidth(self._text_width("Inactive"))
    #
    #     active_state_label.setSizePolicy(QSizePolicy.Preferred,
    #                                      QSizePolicy.Fixed)
    #     return active_state_label
    #
    # def _init_alert_description_label(self) -> QLabel:
    #     alert_description_label = QLabel("[Alert Description]", self)
    #     alert_description_label.setObjectName("alert_description")
    #     alert_description_label.setSizePolicy(QSizePolicy.Expanding,
    #                                           QSizePolicy.Maximum)
    #     return alert_description_label

    def _text_width(self, text: str) -> int:
        # https://stackoverflow.com/a/32078341/8134178
        initial_rect = self.fontMetrics().boundingRect(text)
        improved_rect = self.fontMetrics().boundingRect(initial_rect, 0, text)
        return improved_rect.width()

    @cached_property
    def _max_time_width(self):
        return max(self._text_width(f"{0}{0}:{0}{0}".format(n))
                   for n in range(10))


class AlertLogEntry(AlertLogEntryUI, ClickableMI):

    def __init__(self, alert: Alert, parent: QWidget):
        super().__init__(parent)

        self.alert = alert

        self._init_signals()

        self._populate_alert_info()

    def _init_signals(self):
        self.clicked.connect(self.open_alert_info_dialog)

    def open_alert_info_dialog(self):
        print(f"Opening dialog for {self.alert}")
        ...

    def _populate_alert_info(self) -> None:
        # Alert start time
        start_time_str = self._unix_time_to_tz_time(self.alert.start_time)
        self.start_time_label.setText(start_time_str)

        # Alert end time
        end_time_str = self._unix_time_to_tz_time(self.alert.end_time) \
            if self.alert.end_time \
            else ""
        self.end_time_label.setText(end_time_str)

        # # Active state
        # active_state_str = "Inactive" if alert.end_time else "Active"
        # self.active_state_label.setText(active_state_str)

    def _unix_time_to_tz_time(self, timestamp: float) -> str:
        timezone = "America/Los_Angeles"
        time = pendulum.from_timestamp(timestamp, tz=timezone)
        return time.strftime("%I:%M")  # Maybe use `zz` too?
