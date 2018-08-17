from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths
from .alert_log_entry import AlertLogEntry


class AlertLog(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.alert_log_ui, self)

        self.stream_id = None
        self.alert_widgets = {}  # {alert_id: Alert}

        self.status_poller = api.get_status_poller()

        # Start a QTimer for periodically updating unverified alerts
        self.timer = QTimer()

        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.update_unverified_alerts)
        self.timer.start(1000)

        self.alert_log.setLayout(QVBoxLayout())

    def update_unverified_alerts(self):
        if self.stream_id is None:
            return

        existing_alert_ids = set(self.alert_widgets.keys())

        # TODO: What exactly is a page? How long is a page?
        # Get a page of the most recent alerts
        unverified_alerts = api.get_unverified_alerts(self.stream_id)[::-1]
        unverified_alert_ids = set(alert.id for alert in unverified_alerts)

        # Create new alerts
        new_alerts_ids = unverified_alert_ids - existing_alert_ids
        new_alerts = [alert for alert in unverified_alerts
                      if alert.id in new_alerts_ids]
        if new_alerts:
            statuses = self.status_poller.latest_statuses(self.stream_id)
        for alert in new_alerts:
            # Get the alarm that this alert belongs to
            # noinspection PyUnboundLocalVariable
            # ignoring warning -- in order to be in loop, new_alerts needs to
            # have entries and statuses will be set
            for status in statuses:
                alarm = status.zone.get_alarm(alert.alarm_id)
                if alarm:
                    zone_name = status.zone.name
                    break
            else:
                # If no alarm was found we have an issue
                raise ValueError(f"Alarm ID {alert.alarm_id} "
                                 f"not found for alert ID {alert.id}")

            alert_widget = AlertLogEntry(alert, alarm, zone_name)
            self.alert_log.layout().insertWidget(0, alert_widget)
            self.alert_widgets[alert.id] = alert_widget

        # Update info on existing alerts
        update_alert_ids = unverified_alert_ids & existing_alert_ids
        update_alerts = [alert for alert in unverified_alerts
                         if alert.id in update_alert_ids]
        for alert in update_alerts:
            self.alert_widgets[alert.id].update(alert)
            continue

        # Remove deleted alerts
        deleted_alert_ids = existing_alert_ids - unverified_alert_ids
        for alert_id in deleted_alert_ids:
            self.alert_widgets[alert_id].deleteLater()
            self.alert_widgets.pop(alert_id)

    @pyqtSlot(int)
    def change_stream(self, stream_id):
        """
        Connected to:
        - TODO
        """
        for alert_widget in self.alert_widgets.values():
            alert_widget.deleteLater()
        self.alert_widgets = {}
        self.stream_id = stream_id
