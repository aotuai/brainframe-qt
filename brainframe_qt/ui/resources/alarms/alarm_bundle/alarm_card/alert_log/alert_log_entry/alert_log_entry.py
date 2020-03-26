from typing import List

import typing
from PyQt5.QtCore import Qt, QThread, QMetaObject, Q_ARG, pyqtSlot
from PyQt5.QtWidgets import QFrame, QWidget, QVBoxLayout

from brainframe.client.api.codecs import Alert
from brainframe.client.api.zss_pubsub import zss_publisher, Subscription
from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.mixins.display import ExpandableMI
from brainframe.client.ui.resources.paths import qt_qss_paths

from .alert_header import AlertHeader
from .alert_preview import AlertPreview


class AlertLogEntryUI(QFrame):
    def __init__(self, alert: Alert, parent: QWidget):
        super().__init__(parent)

        self.alert_header = self._init_alert_header()
        self.alert_preview = self._init_alert_preview()

        self._init_layout()
        self._init_style()

    def _init_alert_header(self) -> AlertHeader:
        alert_header = AlertHeader(self)

        return alert_header

    def _init_alert_preview(self) -> AlertPreview:
        alert_preview = AlertPreview(self)

        return alert_preview

    def _init_layout(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.alert_header)
        layout.addWidget(self.alert_preview)

        self.setLayout(layout)

    def _init_style(self) -> None:

        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alert_log_entry_qss)


class AlertLogEntry(AlertLogEntryUI, ExpandableMI):

    def __init__(self, alert: Alert, parent: QWidget):
        super().__init__(alert, parent)

        self.populated_from_server = False

        self.alert = typing.cast(Alert, None)
        self.alert_subscription = typing.cast(Subscription, None)
        self.set_alert(alert)

        self._init_signals()
        self._init_pubsub()

        self.expanded = False

    def _init_signals(self):

        # Toggle alarm preview display on click
        self.alert_header.clicked.connect(self.toggle_expansion)

    def _init_pubsub(self):
        self.alert_subscription = zss_publisher.subscribe_alerts(
            self.handle_alert_stream,
            alert_id=self.alert.id)

        self.destroyed.connect(
            lambda: zss_publisher.unsubscribe(self.alert_subscription))

    def set_alert(self, alert: Alert):

        if self.alert is not None and alert.id != self.alert.id:
            raise ValueError("Changing alert ID is not supported")

        self.alert = alert
        self.alert_header.set_alert(alert)
        self.alert_preview.set_alert(alert)

    def expand(self, expanding: bool):
        self.alert_preview.setVisible(expanding)

        if expanding and not self.populated_from_server:
            self.alert_preview.populate_from_server()
            self.populated_from_server = True

        stylesheet_watcher.update_widget(self)

    @pyqtSlot(object)
    def handle_alert_stream(self, alerts: List[Alert]):

        if QThread.currentThread() != self.thread():
            # Move to the UI Thread
            QMetaObject.invokeMethod(self, self.handle_alert_stream.__name__,
                                     Qt.QueuedConnection,
                                     Q_ARG("PyQt_PyObject", alerts))
            return

        # len(alerts) _should_ == 1
        for alert in alerts:

            # Failsafe, we should be subscribed to just one alert_id
            if self.alert.id != alert.id:
                continue

            # __eq__ is overridden on Codecs
            if alert == self.alert:
                # Nothing to do
                continue

            self.set_alert(alert)
