from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget


class Task(QWidget):

    def __init__(self, task_name, task_type, parent=None):
        super().__init__(parent)

        self.task_name = task_name

        self.main_layout = QHBoxLayout()

        self.icon = QLabel(self)
        self.icon.setPixmap(self._get_icon(task_type))
        self.icon.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.task_name_label = QLabel(task_name)
        self.task_name_label.setAlignment(Qt.AlignCenter)
        self.task_name_label.setSizePolicy(QSizePolicy.Expanding,
                                           QSizePolicy.Minimum)

        # TODO: Use modular resource path approach Alex was talking about
        self.settings_gear = QLabel()
        gear_icon = QPixmap(
            "ui/resources/images/settings_gear/settings_gear.png")
        gear_icon = gear_icon.scaled(32, 32,
                                     transformMode=Qt.SmoothTransformation)
        self.settings_gear.setPixmap(gear_icon)
        self.settings_gear.setSizePolicy(QSizePolicy.Minimum,
                                         QSizePolicy.Minimum)

        self.main_layout.addWidget(self.icon)
        self.main_layout.addWidget(self.task_name_label, Qt.AlignLeft)
        self.main_layout.addWidget(self.settings_gear)

        self.setLayout(self.main_layout)

    @staticmethod
    def _get_icon(zone_type):
        icon_paths = {"region": "ui/resources/images/zone_types/region.png",
                      "line": "ui/resources/images/zone_types/line.jpg",
                      "alarm": "ui/resources/images/zone_types/alarm.jpg"}

        path = icon_paths[zone_type]

        return QPixmap(path).scaled(32, 32,
                                    transformMode=Qt.SmoothTransformation)
