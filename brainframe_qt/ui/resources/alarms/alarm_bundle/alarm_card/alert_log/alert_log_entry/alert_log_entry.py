from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QWidget, QVBoxLayout

from brainframe.client.api.codecs import Alert
from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.mixins.display import ExpandableMI
from brainframe.client.ui.resources.paths import qt_qss_paths

from .alert_header import AlertHeader
from .alert_preview import AlertPreview


class AlertLogEntryUI(QFrame):
    def __init__(self, alert: Alert, parent: QWidget):
        super().__init__(parent)

        self.alert = alert

        self.alert_header = self._init_alert_header()
        self.alert_preview = self._init_alert_preview()

        self._init_layout()
        self._init_style()

    def _init_alert_header(self) -> AlertHeader:
        alert_header = AlertHeader(self.alert, self)

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

        self.alert_preview.set_alert(alert)

        self._init_signals()

        self.expanded = False

    def _init_signals(self):

        # Toggle alarm preview display on click
        self.alert_header.clicked.connect(self.toggle_expansion)

        # Not sure why I need to connect both... but if I don't specify the
        # overloading, either the signal never fires or the slot is never
        # called
        # TODO: Do something?
        self.alert_header.alert_verified[int, bool].connect(lambda: None)
        self.alert_header.alert_verified[int, type(None)].connect(lambda: None)

    def expand(self, expanding: bool):
        # noinspection PyPropertyAccess
        self.alert_preview.setVisible(expanding)

        # noinspection PyPropertyAccess
        if expanding:
            self.alert_preview.populate_from_server()

        stylesheet_watcher.update_widget(self)
