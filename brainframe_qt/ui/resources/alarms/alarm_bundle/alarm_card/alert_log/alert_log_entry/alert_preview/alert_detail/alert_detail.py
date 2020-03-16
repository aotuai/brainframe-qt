from typing import List, Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy

from brainframe.client.api import api, api_errors
from brainframe.client.api.codecs import Alert, ZoneAlarm, \
    ZoneAlarmCountCondition, ZoneAlarmRateCondition, Zone
from brainframe.client.ui.resources import stylesheet_watcher, QTAsyncWorker
from brainframe.client.ui.resources.paths import qt_qss_paths


class AlertDetailUI(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._description = ""

        self.alert_description_label = self._init_alert_description_label()

        self._init_layout()
        self._init_style()

    def _init_alert_description_label(self) -> QLabel:
        alert_description_label = QLabel(self._description, self)
        alert_description_label.setObjectName("alert_description")

        alert_description_label.setWordWrap(True)
        alert_description_label.setSizePolicy(QSizePolicy.Preferred,
                                              QSizePolicy.Expanding)
        alert_description_label.setAlignment(Qt.AlignTop)

        return alert_description_label

    def _init_layout(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(self.alert_description_label)

        self.setLayout(layout)

    def _init_style(self) -> None:

        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alert_detail_qss)

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, description: str):
        self._description = description
        self.alert_description_label.setText(description)


class AlertDetail(AlertDetailUI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

    def set_alert(self, alert: Alert):

        def get_alert_info():
            alarm = api.get_zone_alarm(alert.alarm_id)
            zone = api.get_zone(alarm.zone_id)

            return alert, alarm, zone

        def handle_api_error(error):
            raise error

        QTAsyncWorker(self, get_alert_info,
                      on_success=self.set_alert_info,
                      on_error=handle_api_error) \
            .start()

    def set_alert_info(self, alert_alarm_zone):
        alert: Alert
        alarm: ZoneAlarm
        zone: Zone
        alert, alarm, zone = alert_alarm_zone

        # Create text for alert
        description = ""
        conditions: List[Union[ZoneAlarmCountCondition,
                               ZoneAlarmRateCondition]] \
            = alarm.count_conditions + alarm.rate_conditions
        for condition in conditions:
            text = self.tr("{} in region [{}]")
            text = text.format(repr(condition).strip(), zone.name)
            description += text

        self.description = description
