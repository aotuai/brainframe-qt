import pendulum

from PyQt5.QtWidgets import QLabel, QWidget, QSizePolicy, QHBoxLayout

from brainframe_qt.ui.resources import settings


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
        self._display_timezone = True

    @property
    def time(self) -> pendulum.DateTime:
        """
        :return: The time this label is displaying, in UTC
        """
        return self._time

    @time.setter
    def time(self, time: pendulum.DateTime):
        """
        :param time: The time to display, in UTC
        """
        if time.timezone != pendulum.UTC:
            # We should be working exclusively with UTC times except when
            # displaying to the user or taking in user input. A non-UTC value
            # indicates a bug.
            raise ValueError("The provided time must be in UTC")

        self._time = time

        self._update()

    @property
    def display_timezone(self) -> bool:
        """
        :return: If true, the timezone will be shown to the user in addition
            to the time. By default, this value is True.
        """
        return self._display_timezone

    @display_timezone.setter
    def display_timezone(self, display_timezone: bool):
        """
        :param display_timezone: Whether or not the timezone will be shown to
            the user in addition to the time
        """
        self._display_timezone = display_timezone
        self._update()

    def _update(self):
        display_time = self._time.in_tz(settings.get_user_timezone())
        self.time_label.setText(display_time.format("HH:mm"))
        if self._display_timezone:
            self.timezone_label.setText(display_time.tzname())
        else:
            self.timezone_label.setText("")
