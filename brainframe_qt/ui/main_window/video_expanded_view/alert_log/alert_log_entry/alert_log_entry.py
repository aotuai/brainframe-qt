from datetime import datetime

from PyQt5.QtWidgets import QMessageBox, QWidget
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt

from brainframe.client.ui.resources.paths import qt_ui_paths, image_paths


class AlertLogEntry(QWidget):
    """An entry for the Alert Log"""

    def __init__(self, *, start_time="", end_time=None,
                 alarm_name="", alert_text=None,
                 parent=None):

        super().__init__(parent)
        loadUi(qt_ui_paths.alert_log_entry_ui, self)

        self.start_time = start_time
        self.end_time = end_time
        self.alarm_name = alarm_name
        self.alert_text = alert_text

        self.setToolTip(self.alert_text)

        self.time_label.setText("")
        self.alarm_name_label.setText(alarm_name)

        # Set the alert icon on the left of the log entry
        self.alert_icon_button.setText("")
        pixmap = QPixmap(str(image_paths.alert_icon))
        pixmap = pixmap.scaled(32, 32, transformMode=Qt.SmoothTransformation)
        self.alert_icon_button.setIcon(QIcon(pixmap))

        # Update the time label for the alarm
        self.update_time(self.start_time, self.end_time)

        self.alert_icon_button.clicked.connect(self.display_alert_info)

    def update_time(self, start_time, end_time):
        """Update the alert timestamp of the widget"""

        self.start_time = start_time
        self.end_time = end_time

        alert_start = datetime.fromtimestamp(self.start_time)
        alert_start = alert_start.strftime('%H:%M')
        if self.end_time is not None:
            alert_end = datetime.fromtimestamp(self.end_time)
            alert_end = " to " + alert_end.strftime('%H:%M')
        else:
            alert_end = "(Ongoing)"
        alert_time = alert_start + alert_end

        self.time_label.setText(alert_time)

    def display_alert_info(self):
        """Display a pop-up describing the alert"""
        QMessageBox.information(self, "Alert Information", self.alert_text)
