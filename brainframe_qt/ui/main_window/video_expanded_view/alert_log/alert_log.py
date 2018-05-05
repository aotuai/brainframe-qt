from PyQt5.QtWidgets import QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.uic import loadUi

from .alert_log_entry import AlertLogEntry
from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths


condition_test_map = {'>': "Greater than",
                      '>=': "Greater than or equal to",
                      '<': "Less than",
                      '<=': "Less than or equal to",
                      "=": "Exactly"}


class AlertLog(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        loadUi(qt_ui_paths.alert_log_ui, self)

        self.stream_id = None
        self.alert_widgets = {}  # {alert_id: Alert}

        self.status_poller = api.get_status_poller()

        # Start a QTimer for periodically updating unverified alerts
        self.timer = QTimer()
        # noinspection PyUnresolvedReferences
        # connect is erroneously detected as unresolved
        self.timer.timeout.connect(self.update_unverified_alerts)
        self.timer.start(1000)

        self.alert_log.setLayout(QVBoxLayout())

    def update_unverified_alerts(self):
        if self.stream_id is None:
            return

        unverified = api.get_unverified_alerts(self.stream_id)

        for alert in unverified:

            if alert.id not in self.alert_widgets.get:
                # If the alert widget hasn't been made yet
                alarm = self.status_poller.get_alarm(self.stream_id,
                                                     alert.alarm_id)
                if alarm is None:
                    continue

                zone_name = api.get_zone(self.stream_id, alert.zone_id).name

                alert_text = ""
                for condition in alarm.conditions:
                    condition_str = condition_test_map[condition.test]
                    attr = condition.with_attribute
                    attr = attr + ' ' if attr else ''
                    alert_text += f"{condition_str} {condition.check_value} " \
                                  f"{attr}{condition.with_class_name}(s) " \
                                  f"in region [{zone_name}]\n"
                alert_widget = AlertLogEntry(start_time=alert.start_time,
                                             end_time=alert.end_time,
                                             alarm_name=alarm.name,
                                             alert_text=alert_text)
                self.alert_log.layout().insertWidget(0, alert_widget)
                self.alert_widgets[alert.id] = alert_widget
            else:
                # If the alert already exists, update the information
                alert_widget = self.alert_widgets[alert.id]
                alert_widget.update_time(alert.start_time, alert.end_time)

    @pyqtSlot(int)
    def change_stream(self, stream_id):
        for alert_widget in self.alert_widgets.values():
            alert_widget.deleteLater()
        self.alert_widgets = {}
        self.stream_id = stream_id
