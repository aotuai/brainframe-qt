from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QWidget, QVBoxLayout, QGraphicsView

from brainframe.client.api.codecs import Alert
from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.paths import qt_qss_paths


class AlertPreviewUI(QFrame):
    def __init__(self, alert: Alert, parent: QWidget):
        super().__init__(parent)

        self.alert = alert

        self.alert_image = self._init_alert_image()

        self._init_layout()
        self._init_style()

    def _init_alert_image(self) -> QGraphicsView:
        alert_header = QGraphicsView(self)

        return alert_header

    def _init_layout(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.alert_image)

        self.setLayout(layout)

    def _init_style(self) -> None:

        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alert_preview_qss)


class AlertPreview(AlertPreviewUI):

    def __init__(self, alert: Alert, parent: QWidget):
        super().__init__(alert, parent)
