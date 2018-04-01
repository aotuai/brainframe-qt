from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, pyqtSlot
from PyQt5.uic import loadUi

from visionapp.client.ui.resources.paths import qt_ui_paths
from visionapp.client.api import api


class AlertLog(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        loadUi(qt_ui_paths.alert_log_ui, self)

        self.status_poller = api.get_status_poller()

        # Start a QTimer for periodically updating unverified alerts
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_unverified_alerts)
        self.timer.start(1000)

        self.alert_log.setLayout(QVBoxLayout())

    def update_unverified_alerts(self):
        print("asking for alerts")

    @pyqtSlot(int)
    def change_stream(self, stream_id):
        self.stream_id = stream_id