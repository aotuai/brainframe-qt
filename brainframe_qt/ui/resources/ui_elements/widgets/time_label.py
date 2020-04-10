import pendulum
from pendulum.tz.timezone import Timezone

from PyQt5.QtWidgets import QLabel, QWidget, QSizePolicy, QHBoxLayout


class TimeLabelUI(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.time_label = self._init_time_label()
        self.timezone_label = self._init_timezone_label()

        self._init_layout()

    def _init_time_label(self) -> QLabel:
        time_label = QLabel(self)
        time_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        time_label.setObjectName("time_label")

        time_label.setFixedWidth(self._max_time_width)

        return time_label

    def _init_timezone_label(self) -> QLabel:
        timezone_label = QLabel(self)
        timezone_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        timezone_label.setObjectName("timezone_label")

        return timezone_label

    def _init_layout(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        layout.addWidget(self.time_label)
        layout.addWidget(self.timezone_label)

        self.setLayout(layout)

    def _text_width(self, text: str) -> int:
        # https://stackoverflow.com/a/32078341/8134178
        initial_rect = self.fontMetrics().boundingRect(text)
        improved_rect = self.fontMetrics().boundingRect(initial_rect, 0, text)
        return improved_rect.width()

    @property
    def _max_time_width(self):
        return max(self._text_width(f"{0}{0}:{0}{0}".format(n))
                   for n in range(10))


class TimeLabel(TimeLabelUI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._time = pendulum.DateTime.EPOCH

        # TODO: Make configurable
        self.display_timezone = True

    @property
    def time(self) -> pendulum.DateTime:
        return self._time

    @time.setter
    def time(self, time: pendulum.DateTime):
        self._time = time.in_tz(self.timezone)

        self._update()

    @property
    def timezone(self) -> Timezone:
        return self._time.tz

    @timezone.setter
    def timezone(self, timezone: Timezone):
        self._time.set(tz=timezone)

        self._update()

    def _update(self):
        self.time_label.setText(self.time.format("HH:mm"))
        self.timezone_label.setText(self.time.tzname())

    def change_timezone(self, timezone: pendulum.tz):
        self.time = self.time.in_timezone(timezone)
