from typing import Union

import pendulum
from PyQt5.QtCore import Qt, pyqtProperty, pyqtSlot
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QWidget
from cached_property import cached_property

from brainframe.client.api import api
from brainframe.client.api.codecs import Alert
from brainframe.client.ui.resources import QTAsyncWorker, stylesheet_watcher
from brainframe.client.ui.resources.mixins.mouse import ClickableMI
from brainframe.client.ui.resources.paths import qt_qss_paths
from brainframe.client.ui.resources.ui_elements.buttons import TextIconButton


class AlertLogEntryUI(QFrame):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.start_time_label = self._init_start_time_label()
        self.time_dash_label = self._init_time_dash_label()
        self.end_time_label = self._init_end_time_label()
        self.verified_true_button = self._init_verified_true_button()
        self.verified_false_button = self._init_verified_false_button()

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QHBoxLayout()

        layout.addWidget(self.start_time_label)
        layout.addWidget(self.time_dash_label)
        layout.addWidget(self.end_time_label)
        layout.addStretch()
        layout.addWidget(self.verified_true_button)
        layout.addWidget(self.verified_false_button)

        self.setLayout(layout)

    def _init_style(self):
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alert_log_entry_qss)

    def _init_start_time_label(self) -> QLabel:
        start_time_label = QLabel("00:00", self)
        start_time_label.setObjectName("start_time")

        start_time_label.setFixedWidth(self._max_time_width)

        start_time_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return start_time_label

    def _init_time_dash_label(self) -> QLabel:
        time_dash_label = QLabel("–", self)
        time_dash_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return time_dash_label

    def _init_end_time_label(self) -> QLabel:
        end_time_label = QLabel("00:00", self)
        end_time_label.setObjectName("end_time")

        end_time_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return end_time_label

    def _init_verified_true_button(self) -> TextIconButton:
        verified_true_button = TextIconButton("✔️", self)
        verified_true_button.setObjectName("verified_true_button")

        verified_true_button.setCheckable(True)
        verified_true_button.setFlat(True)

        return verified_true_button

    def _init_verified_false_button(self) -> TextIconButton:
        verified_false_button = TextIconButton("❌", self)
        verified_false_button.setObjectName("verified_false_button")

        verified_false_button.setFlat(True)
        verified_false_button.setCheckable(True)

        return verified_false_button

    def _text_width(self, text: str) -> int:
        # https://stackoverflow.com/a/32078341/8134178
        initial_rect = self.fontMetrics().boundingRect(text)
        improved_rect = self.fontMetrics().boundingRect(initial_rect, 0, text)
        return improved_rect.width()

    @cached_property
    def _max_time_width(self):
        return max(self._text_width(f"{0}{0}:{0}{0}".format(n))
                   for n in range(10))


class AlertLogEntry(AlertLogEntryUI, ClickableMI):

    def __init__(self, alert: Alert, parent: QWidget):
        super().__init__(parent)

        self.alert = alert

        self._init_signals()

        self._populate_alert_info()

    def _init_signals(self):
        self.clicked.connect(self.open_alert_info_dialog)
        self.verified_true_button.clicked[bool].connect(
            self._handle_verification_button_press)
        self.verified_false_button.clicked[bool].connect(
            self._handle_verification_button_press)

    @pyqtProperty(bool)
    def verified(self) -> bool:
        return True

    @pyqtProperty(bool)
    def verified_as(self) -> bool:
        return True

    def open_alert_info_dialog(self):
        print(f"Opening dialog for {self.alert}")
        ...

    def _populate_alert_info(self) -> None:
        # Alert start time
        start_time_str = self._unix_time_to_tz_time(self.alert.start_time)
        self.start_time_label.setText(start_time_str)

        # Alert end time
        end_time_str = self._unix_time_to_tz_time(self.alert.end_time) \
            if self.alert.end_time \
            else ""
        self.end_time_label.setText(end_time_str)

        # Alert verification
        self._set_ui_verification(self.alert.verified_as)

    def set_verification(self, verification: Union[None, bool]):
        self._set_ui_verification(verification)
        QTAsyncWorker(self, api.set_alert_verification,
                      f_args=(self.alert.id,),
                      f_kwargs={"verified_as": verification}) \
            .start()

    def _set_ui_verification(self, verification: Union[None, bool]):
        true_button = self.verified_true_button
        false_button = self.verified_false_button

        verify_true_message = self.tr("Verify alert as True")
        verify_false_message = self.tr("Verify alert as False")
        deverify_true_message = self.tr("Deverify alert as True")
        deverify_false_message = self.tr("Deverify alert as True")

        if verification is None:
            true_button.setChecked(False)
            false_button.setChecked(False)
            true_button.setToolTip(verify_true_message)
            false_button.setToolTip(verify_false_message)
        elif verification is True:
            true_button.setChecked(True)
            false_button.setChecked(False)
            true_button.setToolTip(deverify_true_message)
            false_button.setToolTip(verify_false_message)
        elif verification is False:
            true_button.setChecked(False)
            false_button.setChecked(True)
            true_button.setToolTip(verify_true_message)
            false_button.setToolTip(deverify_false_message)

        stylesheet_watcher.update_widget(self)

    @pyqtSlot(bool)
    def _handle_verification_button_press(self, checked: bool):
        if self.sender() is self.verified_true_button and checked:
            new_verification = True
        elif self.sender() is self.verified_false_button and checked:
            new_verification = False
        else:
            new_verification = None
        self.set_verification(new_verification)

    def _unix_time_to_tz_time(self, timestamp: float) -> str:
        timezone = "America/Los_Angeles"
        time = pendulum.from_timestamp(timestamp, tz=timezone)
        return time.strftime("%I:%M")  # Maybe use `zz` too?
