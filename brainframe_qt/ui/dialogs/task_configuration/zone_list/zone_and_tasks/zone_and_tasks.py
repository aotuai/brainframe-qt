from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QToolButton, QWidget, QGridLayout, QVBoxLayout

from .tasks.task_widget import TaskWidget
from brainframe.client.api import api
from brainframe.client.api.codecs import Zone, ZoneAlarm


class ZoneAndTasks(QWidget):
    """https://stackoverflow.com/a/37927256/8134178"""

    zone_deleted_signal = pyqtSignal(int)

    def __init__(self, zone: Zone, parent=None):
        super().__init__(parent)

        self.zone_name = zone.name
        self.zone_type = TaskWidget.TaskType.in_progress

        self.zone = zone

        self.tasks = []

        self.alarm_area = None
        self.alarm_area_layout = None
        self.toggle_button = None
        self.main_layout = None
        self.zone_widget = None

        self.init_ui()

        # self.setStyleSheet("background-color:black;")

    def init_ui(self):

        self.alarm_area = QWidget(self)
        self.alarm_area_layout = QVBoxLayout(self.alarm_area)
        self.toggle_button = QToolButton(self)
        self.main_layout = QGridLayout(self)

        self.zone_widget = TaskWidget(self.zone_name, self.zone_type, self)
        self.zone_widget.delete_button_pressed.connect(self.zone_deleted)

        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)

        self.alarm_area.setLayout(self.alarm_area_layout)

        self.main_layout.setVerticalSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.toggle_button, 0, 0)
        self.main_layout.addWidget(self.zone_widget, 0, 1)
        self.main_layout.addWidget(self.alarm_area, 1, 1, 1, 1)
        self.setLayout(self.main_layout)

        # self.alarm_area.setStyleSheet("background-color:green;")

    def add_alarm(self, alarm: ZoneAlarm):
        alarm_widget = TaskWidget(alarm.name, TaskWidget.TaskType.alarm)

        # Connect alarm's delete_button_pressed
        alarm_widget.delete_button_pressed.connect(
            lambda alarm=alarm, alarm_widget=alarm_widget: self.remove_alarm(
                alarm, alarm_widget))

        self.alarm_area_layout.addWidget(alarm_widget)

    def remove_alarm(self, alarm: ZoneAlarm, alarm_widget: TaskWidget):
        try:
            self.zone.alarms.remove(alarm)
        except ValueError:
            pass
        alarm_widget.deleteLater()
        self.zone = api.set_zone(self.zone.stream_id, self.zone)

    def zone_deleted(self):
        self.zone_deleted_signal.emit(self.zone.id)

    def update_zone_type(self):
        if len(self.zone.coords) == 0:
            self.zone_widget.set_task_type(TaskWidget.TaskType.in_progress)
        elif len(self.zone.coords) == 2:
            self.zone_widget.set_task_type(TaskWidget.TaskType.line)
        else:
            self.zone_widget.set_task_type(TaskWidget.TaskType.region)
