import pendulum

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QHBoxLayout,
                             QSizePolicy)

from brainframe.client.ui.dialogs import AlertEntryPopup
from brainframe.client.ui.resources.ui_elements.widgets import TimeLabel

# Preload the necessary icons for the AlertLogEntry
pixmap = QPixmap(":/icons/alert")
pixmap = pixmap.scaled(32, 32, transformMode=Qt.SmoothTransformation)
alert_icon = QIcon(pixmap)


class _TimeSpanUI(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.start_label = self._init_time_label("start")
        self.dash_label = self._init_dash_label()
        self.end_label = self._init_time_label("end")

        self._init_layout()

    def _init_time_label(self, name) -> TimeLabel:
        time_label = TimeLabel(self)
        time_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        time_label.setObjectName(f"{name}_label")
        return time_label

    def _init_dash_label(self) -> QLabel:
        dash_label = QLabel("-", self)
        dash_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        dash_label.setObjectName("dash_label")
        return dash_label

    def _init_layout(self) -> None:
        layout = QHBoxLayout()
        layout.setSpacing(1)

        layout.addWidget(self.start_label)
        layout.addWidget(self.dash_label)
        layout.addWidget(self.end_label)
        layout.addStretch()

        self.setLayout(layout)


class _TimeSpan(_TimeSpanUI):
    """Displays a span of time in the format 16:20 PM PST - 16:21 PM PST."""
    pass


class AlertLogEntryUI(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.alert_icon_button = self._init_alert_icon_button()
        self.time_span = self._init_time_span()
        self.alarm_name_label = self._init_alarm_name_label()

        self._init_layout()

    def _init_alert_icon_button(self) -> QPushButton:
        alert_icon_button = QPushButton("", parent=self)
        alert_icon_button.setIcon(alert_icon)
        alert_icon_button.setObjectName("alert_icon_button")
        alert_icon_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return alert_icon_button

    def _init_time_span(self) -> _TimeSpan:
        time_span = _TimeSpan(self)
        time_span.setObjectName("time_span")
        return time_span

    def _init_alarm_name_label(self) -> QLabel:
        alarm_name_label = QLabel("", parent=self)
        alarm_name_label.setObjectName("alarm_name_label")
        return alarm_name_label

    def _init_layout(self) -> None:
        layout = QHBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(9, 0, 9, 0)

        layout.addWidget(self.alert_icon_button)
        layout.setStretch(0, 0)
        layout.addWidget(self.time_span)
        layout.setStretch(1, 1)
        layout.addWidget(self.alarm_name_label)
        layout.setStretch(2, 1)

        self.setLayout(layout)


class AlertLogEntry(AlertLogEntryUI):
    """An entry for the Alert Log"""

    def __init__(self, alert, alarm, zone_name, parent=None):

        super().__init__(parent)

        self.alert = alert
        self.alarm = alarm

        # TODO: Ensure support for more than one condition if implemented
        # Create text for alert
        self.alert_text = ""
        for condition in alarm.count_conditions + alarm.rate_conditions:
            text = self.tr("{} in region [{}]")
            text = text.format(repr(condition), zone_name)
            self.alert_text += text

        self.setToolTip(self.alert_text)

        self.alarm_name_label.setText(self.alarm.name)

        # Set the alert icon on the left of the log entry
        self.alert_icon_button.setText("")
        self.alert_icon_button.setIcon(alert_icon)

        # Update the time label for the alarm
        self.update(alert)

        self.alert_icon_button.clicked.connect(self.display_alert_info)

    def update(self, alert):
        self.alert = alert

        self.time_span.start_label.time = \
            pendulum.from_timestamp(alert.start_time)
        if alert.end_time is not None:
            self.time_span.end_label.time = \
                pendulum.from_timestamp(alert.end_time)
            self.time_span.end_label.setVisible(True)
        else:
            self.time_span.end_label.setVisible(False)

    @pyqtSlot()
    def display_alert_info(self):
        """Display a pop-up describing the alert

        Connected to:
        - AlertLogEntry -- Dynamic
          self.alert_icon_button.clicked
        """
        AlertEntryPopup.show_alert(self.alert_text, self.alert.id, self)
