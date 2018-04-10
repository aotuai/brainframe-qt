from datetime import datetime

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt

from visionapp.client.ui.resources.paths import qt_ui_paths, image_paths


class AlertLogEntry(QWidget):
    def __init__(self, start_time="", alarm_name="", end_time=None, parent=None):
        super().__init__(parent)
        loadUi(qt_ui_paths.alert_log_entry_ui, self)
        self.start_time = start_time
        self.end_time = end_time
        self.alarm_name = alarm_name

        self.time_label.setText("")
        self.alarm_name_label.setText(alarm_name)

        # Set the alert icon on the left of the log entry
        pixmap = QPixmap(str(image_paths.alert_icon))
        pixmap = pixmap.scaled(32, 32, transformMode=Qt.SmoothTransformation)
        self.alert_icon_label.setPixmap(pixmap)

        # Update the time label for the alarm
        self.update_time(self.start_time, self.end_time)

    def update_time(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

        alert_start = datetime.fromtimestamp(self.start_time)
        alert_start = alert_start.strftime('%H:%M')
        alert_end = ""
        if self.end_time is not None:
            alert_end = datetime.fromtimestamp(self.end_time)
            alert_end = " to " + alert_end.strftime('%H:%M')
        alert_time = alert_start + alert_end
        self.time_label.setText(alert_time)
