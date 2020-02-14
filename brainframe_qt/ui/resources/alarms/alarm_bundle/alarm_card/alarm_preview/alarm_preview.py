from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy, QFrame

from brainframe.client.ui.resources.mixins.mouse import ClickableMI
from brainframe.client.ui.resources.paths import qt_qss_paths
from brainframe.client.ui.resources import stylesheet_watcher


class AlarmPreviewUI(QFrame):

    def __init__(self, parent: QWidget):
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
        stream_name_label = QLabel("Alert Name", self)
        stream_name_label.setObjectName("stream_name")
        stream_name_label.setSizePolicy(QSizePolicy.Expanding,
                                        QSizePolicy.Fixed)

        return stream_name_label

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alarm_preview_qss)


class AlarmPreview(AlarmPreviewUI, ClickableMI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)
