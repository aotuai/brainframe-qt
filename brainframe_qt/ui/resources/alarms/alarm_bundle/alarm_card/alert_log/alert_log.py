from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from brainframe.client.ui.resources import stylesheet_watcher
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

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)

        for _ in range(5):
            self.add_alert()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Emit a signal when the widget is clicked"""
        if event.button() != Qt.LeftButton:
            return

        # Mouse release events are triggered on the Widget where the mouse was
        # initially pressed. If the user presses the mouse down, moves the
        # cursor off the widget, and then releases the button, we want to
        # ignore it.
        if not self.rect().contains(event.pos()):
            return

        # noinspection PyUnresolvedReferences
        self.clicked.emit()

    def add_alert(self):
        self.container_widget.layout().addWidget(AlertLogEntry(self))
