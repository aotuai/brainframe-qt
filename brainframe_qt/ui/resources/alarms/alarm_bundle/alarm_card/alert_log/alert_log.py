from typing import List, Optional, overload

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from brainframe.client.api.codecs import Alert
from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.mixins.mouse import ClickableMI
from brainframe.client.ui.resources.paths import qt_qss_paths
from .alert_log_entry import AlertLogEntry


class AlertLogUI(QScrollArea):

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)

        # Initialize widgets
        self.container_widget = self._init_container_widget()
        self._init_viewport_widget()

        self._init_layout()

        self.setWidget(self.container_widget)

        self._init_style()

    def _init_layout(self) -> None:
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        self.container_widget.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.container_widget.setAttribute(Qt.WA_StyledBackground, True)

        self.setWidgetResizable(True)

        stylesheet_watcher.watch(self, qt_qss_paths.alert_log_qss)

    def _init_container_widget(self) -> QWidget:
        container_widget = QWidget(self)
        container_widget.setObjectName("container")
        return container_widget

    def _init_viewport_widget(self) -> None:
        # Give the viewport a name for the stylesheet
        self.viewport().setObjectName("viewport")


class AlertLog(AlertLogUI):
    clicked = pyqtSignal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.alert_log_entries: List[AlertLogEntry] = []

    @overload
    def __getitem__(self, index: int) -> AlertLogEntry:
        """Returns the AlertLogEntry that at the supplied index"""
        ...

    @overload
    def __getitem__(self, alert: Alert) -> AlertLogEntry:
        """Returns the AlertLogEntry that corresponds to the supplied alert"""
        ...

    def __getitem__(self, key) -> AlertLogEntry:
        """Returns the AlertLogEntry for the given key"""
        if isinstance(key, Alert):
            alert = key
            search = (alert_log_entry for alert_log_entry in self
                      if alert_log_entry.alert.id == alert.id)
            try:
                return next(search)
            except StopIteration as exc:
                raise KeyError from exc
        elif isinstance(key, int):
            index = key
            return self.container_widget.layout().itemAt(index)
        else:
            raise TypeError

    def add_alert(self, alert: Alert):
        alert_log_entry = AlertLogEntry(alert, self)
        self.container_widget.layout().addWidget(alert_log_entry)
        self.alert_log_entries.append(alert_log_entry)
