from enum import Enum

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget
)

from visionapp.client.ui.resources.paths import image_paths


class TaskWidget(QWidget):
    # noinspection PyArgumentList
    # PyCharm incorrectly complains
    TaskType = Enum("TaskType", ["region", "line", "alarm", "in_progress"])

    delete_button_pressed = pyqtSignal()

    # TODO: Use .ui files
    def __init__(self, task_name, task_type: TaskType, parent=None):
        super().__init__(parent)

        self.task_name = task_name
        self.task_type = task_type

        self.main_layout = QHBoxLayout()

        self.icon = QLabel(self)
        self.set_task_type(task_type)

        self.icon.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.task_name_label = QLabel(task_name)
        self.task_name_label.setAlignment(Qt.AlignCenter)
        self.task_name_label.setSizePolicy(QSizePolicy.Expanding,
                                           QSizePolicy.Minimum)

        # TODO: Use modular resource path approach Alex was talking about
        self.delete_button = QPushButton()
        trash_icon = QIcon(QPixmap(str(image_paths.trash_icon)))
        self.delete_button.setIcon(trash_icon)
        self.delete_button.setSizePolicy(QSizePolicy.Minimum,
                                         QSizePolicy.Minimum)

        self.main_layout.addWidget(self.icon)
        self.main_layout.addWidget(self.task_name_label, Qt.AlignLeft)
        self.main_layout.addWidget(self.delete_button)

        self.setLayout(self.main_layout)

        # noinspection PyUnresolvedReferences
        # PyCharm incorrectly thinks .connect doesn't exist
        self.delete_button.clicked.connect(self.delete_button_pressed)

    def set_task_type(self, task_type: TaskType):
        self.task_type = task_type
        self.update_icon()

    def update_icon(self):
        self.icon.setPixmap(self._get_icon(self.task_type))

    @classmethod
    def _get_icon(cls, zone_type):
        icon_paths = {cls.TaskType.region: image_paths.region_icon,
                      cls.TaskType.line: image_paths.line_icon,
                      cls.TaskType.alarm: image_paths.alarm_icon,
                      cls.TaskType.in_progress: image_paths.question_mark_icon}

        path = str(icon_paths[zone_type])

        return QPixmap(path).scaled(32, 32,
                                    transformMode=Qt.SmoothTransformation)
