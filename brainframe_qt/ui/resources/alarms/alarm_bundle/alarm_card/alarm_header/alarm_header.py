import typing
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QWidget, \
    QApplication

from brainframe.api import ZoneAlarm
from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.mixins.mouse import ClickableMI
from brainframe.client.ui.resources.paths import qt_qss_paths


class AlarmHeaderUI(QFrame):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.active_text = QApplication.translate("AlarmHeaderUI", "Active")
        self.inactive_text = QApplication.translate(
            "AlarmHeaderUI", "Inactive")

        self.alarm_name_label = self._init_alarm_name_label()
        self.alarm_location_label = self._init_alarm_location_label()
        self.alert_state_label = self._init_alert_state_label()

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(self.alarm_name_label)
        layout.addWidget(self.alarm_location_label)
        layout.addStretch()
        layout.addWidget(self.alert_state_label)

        self.setLayout(layout)

    def _init_alarm_name_label(self) -> QLabel:
        alarm_name_label = QLabel("Alarm Name", self)
        alarm_name_label.setObjectName("alarm_name")
        return alarm_name_label

    def _init_alarm_location_label(self) -> QLabel:
        alarm_location_label = QLabel("in [Alarm Location]", self)
        alarm_location_label.setObjectName("alarm_location")
        return alarm_location_label

    def _init_alert_state_label(self) -> QLabel:
        alert_state_label = QLabel(self.inactive_text, self)
        alert_state_label.setObjectName("alert_state")

        return alert_state_label

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Use a fixed amount of vertical space
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        stylesheet_watcher.watch(self, qt_qss_paths.alarm_header_qss)


class AlarmHeader(AlarmHeaderUI, ClickableMI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.alarm = typing.cast(ZoneAlarm, None)

    def set_alarm(self, alarm: ZoneAlarm, alarm_location: str = None):
        self.alarm = alarm
        self.alarm_name_label.setText(alarm.name)

        if alarm_location is None:
            self.alarm_location_label.setHidden(True)
        else:
            self.alarm_location_label.setText(alarm_location)

    def set_active(self, active: bool) -> None:
        text = self.active_text if active else self.inactive_text
        self.alert_state_label.setText(text)
