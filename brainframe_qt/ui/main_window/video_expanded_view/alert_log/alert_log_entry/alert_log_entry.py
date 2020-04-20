from datetime import datetime

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.uic import loadUiType

from brainframe.client.ui.dialogs import AlertEntryPopup
from brainframe.client.ui.resources import qt_resources
from brainframe.client.ui.resources.paths import qt_ui_paths

# Preload the necessary icons for the AlertLogEntry
pixmap = QPixmap(":/icons/alert")
pixmap = pixmap.scaled(32, 32, transformMode=Qt.SmoothTransformation)
alert_icon = QIcon(pixmap)

# Preload & parse the UI file into memory, for performance reasons
_Form, _Base = loadUiType(qt_ui_paths.alert_log_entry_ui)


class AlertLogEntry(_Form, _Base):
    """An entry for the Alert Log"""

    def __init__(self, alert, alarm, zone_name, parent=None):

        super().__init__(parent)
        self.setupUi(self)

        self.alert = alert
        self.alarm = alarm

        # TODO: Ensure support for more than one condition if implemented
        # Create text for alert
        self.alert_text = ""
        for condition in alarm.count_conditions + alarm.rate_conditions:
            text = self.tr("{} in region [{}]")
            text = text.format(repr(condition), zone_name)
            self.alert_text += text

        self.setToolTip(self.alert_text)

        self.time_label.setText("")
        self.alarm_name_label.setText(self.alarm.name)

        # Set the alert icon on the left of the log entry
        self.alert_icon_button.setText("")
        self.alert_icon_button.setIcon(alert_icon)

        # Update the time label for the alarm
        self.update(alert)

        self.alert_icon_button.clicked.connect(self.display_alert_info)

    def update(self, alert):

        self.alert = alert

        alert_start = datetime.fromtimestamp(alert.start_time)
        alert_start = alert_start.strftime('%H:%M')
        if alert.end_time is not None:
            alert_end = datetime.fromtimestamp(alert.end_time)
            alert_end = alert_end.strftime('%H:%M')
        else:
            alert_end = self.tr("(Ongoing)")
        alert_time = self.tr("{} to {}").format(alert_start, alert_end)

        self.time_label.setText(alert_time)

    @pyqtSlot()
    def display_alert_info(self):
        """Display a pop-up describing the alert

        Connected to:
        - AlertLogEntry -- Dynamic
          self.alert_icon_button.clicked
        """
        AlertEntryPopup.show_alert(self.alert_text, self.alert.id, self)
