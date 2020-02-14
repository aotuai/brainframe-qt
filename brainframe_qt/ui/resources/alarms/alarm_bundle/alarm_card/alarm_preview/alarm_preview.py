from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy, QFrame

from brainframe.client.ui.resources.paths import qt_qss_paths
from brainframe.client.ui.resources import stylesheet_watcher


class AlarmPreviewUI(QFrame):

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)

        self.stream_name_label = self._init_stream_name_label()
        self.alert_state_label = self._init_alert_state_label()

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QHBoxLayout()
        layout.addWidget(self.stream_name_label)
        layout.addWidget(self.alert_state_label)

        self.setLayout(layout)

    def _init_alert_state_label(self) -> QLabel:
        alert_state_label = QLabel("Inactive", self)
        alert_state_label.setObjectName("alert_state")
        alert_state_label.setSizePolicy(QSizePolicy.Expanding,
                                        QSizePolicy.Fixed)

        return alert_state_label

    def _init_stream_name_label(self) -> QLabel:
        stream_name_label = QLabel("Stream 1", self)
        stream_name_label.setObjectName("stream_name")
        stream_name_label.setSizePolicy(QSizePolicy.Expanding,
                                        QSizePolicy.Fixed)

        return stream_name_label

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alarm_preview_qss)


class AlarmPreview(AlarmPreviewUI):

    clicked = pyqtSignal()

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Emit a signal when the widget is clicked"""
        if event.button() != Qt.LeftButton:
            return

        # Mouse release events are triggered on the Widget where the mouse was
        # initially pressed. If the user presses the mouse down, moves the
        # cursor off the widget, and then releases the button, we want to ignore
        # it.
        if not self.rect().contains(event.pos()):
            return

        # noinspection PyUnresolvedReferences
        self.clicked.emit()
