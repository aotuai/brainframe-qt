from PyQt5.QtCore import (
    QParallelAnimationGroup,
    QPropertyAnimation,
    QAbstractAnimation,
    Qt
)
from PyQt5.QtWidgets import (
    QScrollArea,
    QToolButton,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QSizePolicy
)

from .tasks.task_widget import TaskWidget
from .tasks.zone_widget import ZoneWidget


class ZoneAndTasks(QWidget):
    """https://stackoverflow.com/a/37927256/8134178"""

    def __init__(self, zone_name, zone_type, parent=None):
        super().__init__(parent)

        self.zone_name = zone_name
        self.zone_type = zone_type

        self.tasks = []

        self.toggle_animation = None
        self.alarm_area = None
        self.alarm_area_layout = None
        self.toggle_button = None
        self.main_layout = None
        self.zone = None

        self.init_ui()

    def init_ui(self):
        self.toggle_animation = QParallelAnimationGroup()
        self.alarm_area = QScrollArea()
        self.alarm_area_layout = QVBoxLayout()
        self.toggle_button = QToolButton()
        self.main_layout = QGridLayout()
        self.zone = ZoneWidget(self.zone_name, self.zone_type)

        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)

        self.alarm_area.setLayout(self.alarm_area_layout)

        # Expand only vertically
        self.alarm_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Start out collapsed
        self.alarm_area.setMaximumHeight(0)
        self.alarm_area.setMinimumHeight(0)

        # Let widget grow and shrink with its content
        self.toggle_animation.addAnimation(QPropertyAnimation(self,
                                                              b"minimumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self,
                                                              b"maximumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self.alarm_area,
                                                              b"maximumHeight"))

        self.main_layout.setVerticalSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.toggle_button, 0, 0)
        self.main_layout.addWidget(self.zone, 0, 1)
        self.main_layout.addWidget(self.alarm_area, 1, 1, 1, 1)
        self.setLayout(self.main_layout)

        self.toggle_button.clicked.connect(self.animate)

    def animate(self, checked):
        self.toggle_button.setArrowType(
            Qt.DownArrow if checked else Qt.RightArrow)

        direction = QAbstractAnimation.Forward if checked \
            else QAbstractAnimation.Backward

        self.toggle_animation.setDirection(direction)
        self.toggle_animation.start()

    def set_content_layout(self, animation_duration=300):
        # Is this equivalent to `delete alarm_area.layout` in C++?
        self.alarm_area.destroy()
        self.alarm_area.setLayout(self.alarm_area_layout)

        collapsed_height = self.sizeHint().height() \
            - self.alarm_area.maximumHeight()

        content_height = self.alarm_area_layout.sizeHint().height()

        frames = self.toggle_animation.animationCount() - 1
        for i in range(frames):
            spoiler_animation = self.toggle_animation.animationAt(i)
            spoiler_animation.setDuration(animation_duration)
            spoiler_animation.setStartValue(collapsed_height)
            spoiler_animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggle_animation.animationAt(frames)
        content_animation.setDuration(animation_duration)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)

    def add_alarm(self, alarm: Alarm):
        print("adding alarm")
        alarm_widget = TaskWidget(alarm.alarm_name, TaskWidget.TaskType.alarm)
        self.alarm_area_layout.addWidget(alarm_widget)

        self.set_content_layout()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    zone_and_tasks = ZoneAndTasks("Locker Area", ZoneAndTasks.TaskType.region)
    zone_and_tasks.show()

    app.exec_()
