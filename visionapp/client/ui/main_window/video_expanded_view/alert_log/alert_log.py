from datetime import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, pyqtSlot
from PyQt5.uic import loadUi

from visionapp.client.ui.resources.paths import qt_ui_paths
from .alert_log_entry.alert_log_entry import AlertLogEntry
from visionapp.client.api import api


class AlertLog(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        loadUi(qt_ui_paths.alert_log_ui, self)

        self.stream_id = None
        self.alert_widgets = {}  # {alert_id: Alert}

        self.status_poller = api.get_status_poller()

        # Start a QTimer for periodically updating unverified alerts
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_unverified_alerts)
        self.timer.start(1000)

        self.alert_log.setLayout(QVBoxLayout())

    def update_unverified_alerts(self):
        if self.stream_id is None: return

        unverified = api.get_unverified_alerts(self.stream_id)

        for alert in unverified:
            if alert.id in self.alert_widgets:
                continue
            alarm = self.status_poller.get_alarm(self.stream_id, alert.alarm_id)
            alarm_text = alarm.name
            alert_start = datetime.fromtimestamp(alert.start_time)
            alert_start = alert_start.strftime('%H:%M')
            alert_end = ""
            if alert.end_time is not None:
                alert_end = datetime.fromtimestamp(alert.end_time)
                alert_end = " to " + alert_end.strftime('%H:%M')
            alert_time = alert_start + alert_end

            alert_widget = AlertLogEntry(alert_time, alarm_text)
            self.alert_log.layout().addWidget(alert_widget)
            self.alert_widgets[alert.id] = alert_widget

    @pyqtSlot(int)
    def change_stream(self, stream_id):
        for alert_widget in self.alert_widgets.values():
            alert_widget.deleteLater()
        self.alert_widgets = {}
        self.stream_id = stream_id
