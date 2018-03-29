from PyQt5.QtCore import (
    QParallelAnimationGroup,
    QPropertyAnimation,
    QAbstractAnimation,
    Qt
)
from PyQt5.QtWidgets import (
    QToolButton,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QSizePolicy
)

from .tasks.task_widget import TaskWidget
from visionapp.client.api.codecs import Zone
from visionapp.client.ui.resources.datatypes.alarm import Alarm


class ZoneAndTasks(QWidget):
    """https://stackoverflow.com/a/37927256/8134178"""

    def __init__(self, zone, parent=None):
        super().__init__(parent)

        self.zone_name = zone.name
        self.zone_type = TaskWidget.TaskType.in_progress

        self.zone = zone

        self.tasks = []

        self.toggle_animation = None
        self.alarm_area = None
        self.alarm_area_layout = None
        self.toggle_button = None
        self.main_layout = None
        self.zone_widget = None

        self.init_ui()

        # self.setStyleSheet("background-color:black;")

    def init_ui(self):

        # Run multiple animations in parallel (ie. at same time)
        self.toggle_animation = QParallelAnimationGroup()

        self.alarm_area = QWidget(self)
        self.alarm_area_layout = QVBoxLayout(self.alarm_area)
        self.toggle_button = QToolButton(self)
        self.main_layout = QGridLayout(self)

        self.zone_widget = TaskWidget(self.zone_name, self.zone_type, self)

        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)

        self.alarm_area_layout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        self.alarm_area.setLayout(self.alarm_area_layout)

        # Expand only vertically
        self.alarm_area.setSizePolicy(QSizePolicy.Expanding,
                                      QSizePolicy.Expanding)

        # Start out with alarm_area at 0 height
        # Both min and max need to be set to 0 as min overrides max when min>max
        self.alarm_area.setMinimumHeight(0)
        self.alarm_area.setMaximumHeight(0)

        # Let widget grow and shrink with its content
        # QPropertyAnimations change the string property variably from
        # startValue to endValue in a duration
        # eg. self.minimumHeight or self.alarm_area.maximumHeight

        # spoiler_animation
        self.toggle_animation.addAnimation(QPropertyAnimation(self,
                                                              b"minimumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self,
                                                              b"maximumHeight"))
        # content_animation
        self.toggle_animation.addAnimation(QPropertyAnimation(self.alarm_area,
                                                              b"maximumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self.alarm_area,
                                                              b"minimumHeight"))

        self.main_layout.setVerticalSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.toggle_button, 0, 0)
        self.main_layout.addWidget(self.zone_widget, 0, 1)
        self.main_layout.addWidget(self.alarm_area, 1, 1, 1, 1)
        self.setLayout(self.main_layout)

        self.setMinimumHeight(self.sizeHint().height())
        self.setMaximumHeight(self.sizeHint().height())

        # self.alarm_area.setStyleSheet("background-color:green;")

        # noinspection PyUnresolvedReferences
        self.toggle_button.clicked.connect(self.animate)

    def animate(self, checked):
        self.toggle_button.setArrowType(
            Qt.DownArrow if checked else Qt.RightArrow)

        direction = QAbstractAnimation.Forward if checked \
            else QAbstractAnimation.Backward

        self.toggle_animation.setDirection(direction)
        self.toggle_animation.start()

    def set_content_layout(self, animation_duration=300):
        """Update the layout and animations

        Update the layout and animations to make use of the new height after the
        addition of new content to the layout
        # """
        # Is this equivalent to `delete alarm_area.layout` in C++?
        self.alarm_area.destroy()
        self.alarm_area.setLayout(self.alarm_area_layout)

        collapsed_height = self.sizeHint().height() \
                           - self.alarm_area.maximumHeight()

        content_height = self.alarm_area_layout.sizeHint().height()

        self.alarm_area.setMinimumHeight(content_height)
        self.alarm_area.setMinimumHeight(content_height)
        self.setMinimumHeight(collapsed_height + content_height)
        self.setMaximumHeight(collapsed_height + content_height)

        # Animate the maximumHeight of the widget to hide the alarm_area
        for i in range(2):
            spoiler_animation = self.toggle_animation.animationAt(i)
            spoiler_animation.setDuration(animation_duration)
            spoiler_animation.setStartValue(collapsed_height)
            spoiler_animation.setEndValue(collapsed_height + content_height)

        # Animate the maximumHeight of the alarm_area widget itself
        for i in range(2, 4):
            content_animation = self.toggle_animation.animationAt(i)
            content_animation.setDuration(animation_duration)
            content_animation.setStartValue(0)
            content_animation.setEndValue(content_height)

    def add_alarm(self, alarm: Alarm):
        alarm_widget = TaskWidget(alarm.alarm_name, TaskWidget.TaskType.alarm,
                                  self.alarm_area)

        self.alarm_area_layout.addWidget(alarm_widget)

        self.set_content_layout()

    def update_zone_type(self):
        if len(self.zone.coords) == 0:
            self.zone_widget.set_task_type(TaskWidget.TaskType.in_progress)
        elif len(self.zone.coords) == 2:
            self.zone_widget.set_task_type(TaskWidget.TaskType.line)
        else:
            self.zone_widget.set_task_type(TaskWidget.TaskType.region)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    zone_and_tasks = ZoneAndTasks(Zone(name="Test Zone", coords=[]))
    zone_and_tasks.show()

    app.exec_()
