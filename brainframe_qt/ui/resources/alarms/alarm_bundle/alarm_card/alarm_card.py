import typing
from typing import List, Optional

from PyQt5.QtCore import QMetaObject, Q_ARG, Qt, pyqtProperty, pyqtSlot, \
    QThread
from PyQt5.QtWidgets import QFrame, QLayout, QSizePolicy, QVBoxLayout, QWidget

from brainframe.client.api_helpers import api
from brainframe.api.codecs import Alert, ZoneAlarm
from brainframe.client.api_helpers.zss_pubsub import zss_publisher
from brainframe.client.ui.resources import QTAsyncWorker, stylesheet_watcher
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
        self.MAX_ALERTS = 50

        self.stream_id = typing.cast(int, None)
        self._stream_name = typing.cast(str, None)

        self.zone_id: Optional[int] = None
        self._zone_name: Optional[str] = None

        self.alarm_header.set_alarm(self.alarm)
        self._init_alert_log_history()

        self._init_signals()

    def expand(self, expanding: bool):
        self.alert_log.setVisible(expanding)
        stylesheet_watcher.update_widget(self)

    def iterable_layout(self) -> QLayout:
        return self.alert_log.layout()

    def _init_signals(self):
        self.alarm_header.clicked.connect(self.toggle_expansion)
        self.alert_log.alert_activity_changed.connect(self._set_alert_active)

        subscription = zss_publisher.subscribe_alerts(
            self.handle_alert_stream,
            alarm_id=self.alarm.id)
        self.destroyed.connect(lambda: zss_publisher.unsubscribe(subscription))

    def _init_alert_log_history(self) -> None:

        self.alert_log.max_alerts = self.MAX_ALERTS

        def handle_success(alerts_and_count):
            alerts: List[Alert]
            _count: int
            alerts, _count = alerts_and_count
            self.handle_alert_stream(alerts)

        def handle_error(err):
            raise err

        QTAsyncWorker(self, api.get_alerts,
                      f_kwargs={"alarm_id": self.alarm.id,
                                "limit": self.MAX_ALERTS,
                                "offset": 0},
                      on_success=handle_success,
                      on_error=handle_error) \
            .start()

    @pyqtSlot(object)
    def handle_alert_stream(self, alerts: List[Alert]):
        """Add new alerts when the ZSS gets them"""

        if QThread.currentThread() != self.thread():
            # Move to the UI Thread
            QMetaObject.invokeMethod(self, self.handle_alert_stream.__name__,
                                     Qt.QueuedConnection,
                                     Q_ARG("PyQt_PyObject", alerts))
            return

        for alert in alerts:
            if not self.alert_log.contains_alert(alert):
                self.alert_log.add_alert(alert)

    @pyqtProperty(bool)
    def alert_active(self) -> bool:
        return self._alert_active

    def _set_alert_active(self, alert_active: bool) -> None:
        """Private setter for alert_active property"""
        self._alert_active = alert_active
        self.alarm_header.set_active(alert_active)
        stylesheet_watcher.update_widget(self)


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
