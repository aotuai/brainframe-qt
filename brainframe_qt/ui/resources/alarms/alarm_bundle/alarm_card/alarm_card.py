from typing import List, Optional, Tuple
import typing

from PyQt5.QtCore import Qt, pyqtProperty
from PyQt5.QtWidgets import QFrame, QLayout, QSizePolicy, QVBoxLayout, QWidget

from brainframe.client.api import api
from brainframe.client.api.codecs import Alert, ZoneAlarm
from brainframe.client.ui.resources import stylesheet_watcher, QTAsyncWorker
# TODO: Change to relative imports?
from brainframe.client.ui.resources.alarms.alarm_bundle.alarm_card.alarm_header \
    import AlarmHeader
from brainframe.client.ui.resources.alarms.alarm_bundle.alarm_card.alert_log \
    import AlertLog
from brainframe.client.ui.resources.mixins.data_structure import IterableMI
from brainframe.client.ui.resources.mixins.display import ExpandableMI
from brainframe.client.ui.resources.paths import qt_qss_paths


class AlarmCardUI(QFrame):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.alarm_header = self._init_alarm_header()
        self.alert_log = self._init_alert_log()

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.alarm_header)
        layout.addWidget(self.alert_log)

        self.setLayout(layout)

    def _init_style(self):
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Fixed height will allow cards to be proper size (i.e. expanded
        # AlertLog
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        stylesheet_watcher.watch(self, qt_qss_paths.alarm_card_qss)

    def _init_alarm_header(self) -> AlarmHeader:
        alarm_header = AlarmHeader(self)
        return alarm_header

    def _init_alert_log(self) -> AlertLog:
        alert_log = AlertLog(self)
        return alert_log


class AlarmCard(AlarmCardUI, ExpandableMI, IterableMI):

    def __init__(self, alarm: ZoneAlarm, parent: QWidget):
        # Properties
        self._alert_active = False

        super().__init__(parent)

        self.alarm = alarm

        self.stream_id = typing.cast(int, None)
        self._stream_name = typing.cast(str, None)

        self.zone_id: Optional[int] = None
        self._zone_name: Optional[str] = None

        self.alarm_header.set_alarm(self.alarm)
        self._init_alert_log_history()

        self._init_signals()

    def _init_signals(self):
        self.alarm_header.clicked.connect(self.toggle_expansion)

    @pyqtProperty(bool)
    def alert_active(self) -> bool:
        return self._alert_active

    def _set_alert_active(self, alert_active: bool) -> None:
        """Private setter for alert_active property"""
        self._alert_active = alert_active
        stylesheet_watcher.update_widget(self)

    def expansion_changed(self):
        # noinspection PyPropertyAccess
        self.alert_log.setVisible(self.expanded)
        stylesheet_watcher.update_widget(self)

    def iterable_layout(self) -> QLayout:
        return self.alert_log.layout()

    def add_alert(self, alert: Alert):
        # Additions should always be the most recent alert
        self._set_alert_active(alert.end_time is None)
        self.alert_log.add_alert(alert)

    def update_alert(self, alert: Alert):
        if self.alert_log[0].alert.id == alert.id:
            self._set_alert_active((alert.end_time is None))
        self.alert_log.update_alert(alert)

    def _init_alert_log_history(self) -> None:
        QTAsyncWorker(self, api.get_alerts,
                      f_kwargs={"alarm_id": self.alarm.id},
                      on_success=self._populate_alert_log,
                      on_error=self._handle_get_alerts_error) \
            .start()

    def _populate_alert_log(self, alerts_and_count: Tuple[List[Alert], int]):
        alerts, total_count = alerts_and_count

        # Populate log oldest -> newest
        for alert in reversed(alerts):
            self.add_alert(alert)

    def _handle_get_alerts_error(self, err):
        raise err

    # @property
    # def stream_name(self):
    #     if not self._stream_name:
    #         # TODO: Run in another thread
    #         stream: StreamConfiguration \
    #             = api.get_stream_configuration(stream_id=self.stream_id)
    #         self._stream_name = stream.name
    #     return self._stream_name
    #
    # @property
    # def zone_name(self):
    #     if self.zone_id is None:
    #         return None
    #     if not self._zone_name:
    #         # TODO: Run in another thread
    #         zone: Zone = api.get_zone(zone_id=self.zone_id)
    #         self._zone_name = zone.name
    #     return self._zone_name


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication([])

    window = QWidget()
    window.setAttribute(Qt.WA_StyledBackground, True)

    window.setLayout(QVBoxLayout())

    zone_alarm = ZoneAlarm(
        name="Too Many Shuchs",
        count_conditions=None,
        rate_conditions=None,
        use_active_time=False,
        active_start_time=None,
        active_end_time=None
    )

    window.layout().addWidget(AlarmCard(zone_alarm, parent=window))

    window.show()

    app.exec_()
