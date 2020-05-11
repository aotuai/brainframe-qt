from typing import Dict, Iterable, List, Tuple
import logging

from requests.exceptions import RequestException
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.uic import loadUi

from brainframe.client.api_helpers import api
from brainframe.api import api_errors
from brainframe.api.codecs import Alert, Zone, ZoneAlarm
from brainframe.client.ui.resources import QTAsyncWorker
from brainframe.client.ui.resources.paths import qt_ui_paths

from .alert_log_entry import AlertLogEntry


class AlertLog(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.alert_log_ui, self)

        self.stream_id = None
        self.alert_widgets: Dict[int, AlertLogEntry] = {}  # key = alert_id

        # Start a QTimer for periodically updating unverified alerts
        self.timer = QTimer()
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.sync_alerts_with_server)
        self.timer.start(1000)

        self.alert_log.setLayout(QVBoxLayout())

    def change_stream(self, stream_id):
        self.stream_id = stream_id
        self._delete_alerts_by_id(self.alert_widgets.keys())
        self.sync_alerts_with_server()

    def sync_alerts_with_server(self):

        # Important. Used in set_alerts_checked
        stream_id = self.stream_id

        if stream_id is None:
            self._delete_alerts_by_id(self.alert_widgets.keys())
            return

        def get_alerts_from_server():

            try:
                # Get a page of the 100 most recent alerts
                server_side_alerts, total_count = api.get_alerts(
                    stream_id=stream_id,
                    limit=100,
                    offset=0)
            except api_errors.StreamConfigNotFoundError:
                # Return an empty list. The callback will delete all the
                # existing Alerts from the UI
                return []
            except RequestException as ex:
                logging.error(f"While polling for alerts: {ex}")
                return None

            # We want it oldest to newest
            unverified_alerts = server_side_alerts[::-1]

            return unverified_alerts

        def set_alerts_checked(alerts: List[Alert]):
            # Make sure that the stream_id was not changed while the API call
            # was blocked
            if self.stream_id != stream_id:
                # Just wait for the next run of the timer
                return

            if alerts is None:
                # An error occurred while fetching alerts
                return

            # If no change to stream_id, then use the results from the API
            self._set_alerts(alerts)

        QTAsyncWorker(self, get_alerts_from_server,
                      on_success=set_alerts_checked) \
            .start()

    def _set_alerts(self, server_side_alerts: List[Alert]):

        def get_alarms_and_zones():
            try:
                alarms: List[ZoneAlarm] = api.get_zone_alarms(self.stream_id)
                zones: List[Zone] = api.get_zones(self.stream_id)
            except api_errors.StreamConfigNotFoundError:
                return None
            except RequestException as ex:
                logging.error(f"Error while getting alarms and zones for "
                              f"alerts: {ex}")
                return None
            alarm_dict = {alarm.id: alarm for alarm in alarms}
            zone_dict = {zone.id: zone for zone in zones}

            return alarm_dict, zone_dict

        def edit_alerts(alarms_and_zones: Tuple[Dict[int, ZoneAlarm],
                                                Dict[int, Zone]]):

            if alarms_and_zones is None:
                # This occurs when a stream was deleted while the api_helpers call
                # for getting alarms/zones was being called, or if a connection
                # error occurred.
                # We're relying on sync_alerts_with_server to clean up
                # the Alert Log
                return None

            alarms, zones = alarms_and_zones

            existing_alert_ids = set(self.alert_widgets.keys())
            server_side_alert_ids = {alert.id for alert in server_side_alerts}

            # Create new alerts
            new_alerts_ids = server_side_alert_ids - existing_alert_ids
            new_alerts = [alert for alert in server_side_alerts
                          if alert.id in new_alerts_ids]
            self._add_alerts(new_alerts, alarms, zones)

            # Update info on existing alerts
            update_alert_ids = server_side_alert_ids & existing_alert_ids
            update_alerts = [alert for alert in server_side_alerts
                             if alert.id in update_alert_ids]
            self._update_alerts(update_alerts)

            # Remove deleted alerts
            deleted_alert_ids = existing_alert_ids - server_side_alert_ids
            self._delete_alerts_by_id(deleted_alert_ids)

        QTAsyncWorker(self, get_alarms_and_zones, on_success=edit_alerts) \
            .start()

    def _add_alerts(self, alerts: Iterable[Alert],
                    alarms: Dict[int, ZoneAlarm],
                    zones: Dict[int, Zone]):

        for alert in alerts:
            try:
                alarm: ZoneAlarm = alarms[alert.alarm_id]
                zone: Zone = zones[alarm.zone_id]
            except KeyError:
                # Assume the alarm or zone was deleted elsewhere and
                # that we can ignore the alert
                continue

            alert_widget = AlertLogEntry(alert, alarm, zone.name)
            self.alert_log.layout().insertWidget(0, alert_widget)
            self.alert_widgets[alert.id] = alert_widget

    def _delete_alerts_by_id(self, alert_ids: Iterable[int]):
        for alert_id in list(alert_ids):
            self.alert_widgets.pop(alert_id).deleteLater()

    def _update_alerts(self, alerts: Iterable[Alert]):
        for alert in alerts:
            self.alert_widgets[alert.id].update(alert)
