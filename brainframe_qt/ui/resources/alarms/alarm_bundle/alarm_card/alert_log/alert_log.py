from typing import List, Optional

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


class AlertLog(AlertLogUI, ClickableMI):
    clicked = pyqtSignal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.alert_log_entries: List[AlertLogEntry] = []

    def add_alert(self, alert: Alert):
        alert_log_entry = AlertLogEntry(alert, self)
        self.container_widget.layout().addWidget(alert_log_entry)
        self.alert_log_entries.append(alert_log_entry)
