import logging
import typing
from typing import Union

import pendulum
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QAbstractButton, QButtonGroup, QFrame, \
    QHBoxLayout, QLabel, QSizePolicy, QWidget

from brainframe.client.api import api_errors
from brainframe.client.api.codecs import Alert
from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.api_pubsub import async_api_pubsub
from brainframe.client.ui.resources.mixins.mouse import ClickableMI
from brainframe.client.ui.resources.paths import qt_qss_paths
from brainframe.client.ui.resources.ui_elements.buttons import TextIconButton
from brainframe.client.ui.resources.ui_elements.widgets import TimeLabel


class AlertHeaderUI(QFrame):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.start_time_label = self._init_start_time_label()
        self.time_dash_label = self._init_time_dash_label()
        self.end_time_label = self._init_end_time_label()

        self.verification_button_group = self._init_verification_button_group()
        self.verified_true_button = self._init_verified_true_button()
        self.verified_false_button = self._init_verified_false_button()

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QHBoxLayout()
        layout.setSpacing(2)

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

        stylesheet_watcher.watch(self, qt_qss_paths.alert_header_qss)

    def _init_start_time_label(self) -> TimeLabel:
        start_time_label = TimeLabel(self)
        start_time_label.setObjectName("start_time")

        return start_time_label

    def _init_time_dash_label(self) -> QLabel:
        time_dash_label = QLabel("–", self)
        time_dash_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return time_dash_label

    def _init_end_time_label(self) -> TimeLabel:
        end_time_label = TimeLabel(self)
        end_time_label.setObjectName("end_time")

        return end_time_label

    def _init_verification_button_group(self) -> QButtonGroup:
        verification_button_group = QButtonGroup(self)
        verification_button_group.setExclusive(False)

        return verification_button_group

    def _init_verified_true_button(self) -> TextIconButton:
        verified_true_button = TextIconButton("✔️", self)
        verified_true_button.setObjectName("verified_true_button")

        verified_true_button.setCheckable(True)
        verified_true_button.setFlat(True)

        # Disable until we have an alert set for the widget
        verified_true_button.setDisabled(True)

        self.verification_button_group.addButton(verified_true_button)

        return verified_true_button

    def _init_verified_false_button(self) -> TextIconButton:
        verified_false_button = TextIconButton("❌", self)
        verified_false_button.setObjectName("verified_false_button")

        verified_false_button.setFlat(True)
        verified_false_button.setCheckable(True)

        # Disable until we have an alert set for the widget
        verified_false_button.setDisabled(True)

        self.verification_button_group.addButton(verified_false_button)

        return verified_false_button


class AlertHeader(AlertHeaderUI, ClickableMI):
    alert_verified = pyqtSignal([int, type(None)], [int, bool])

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.alert = typing.cast(Alert, None)

        self._init_signals()

    def _init_signals(self):
        self.verification_button_group.buttonClicked \
            .connect(self._alert_verified)

    def set_alert(self, alert: Alert):

        # TODO: Find a more robust way to do this
        verification_changed = (self.alert is None and alert is not None) \
                               or (self.alert.verified_as != alert.verified_as)

        timespan_changed = (self.alert is None and alert is not None) \
                           or (self.alert.start_time != alert.start_time) \
                           or (self.alert.end_time != alert.end_time)

        self.alert = alert

        self.verified_false_button.setDisabled(self.alert is None)
        self.verified_true_button.setDisabled(self.alert is None)

        if verification_changed:
            self._set_ui_verification()
        if timespan_changed:
            self._set_ui_timespan()

    def _set_ui_timespan(self):
        # Alert start time
        start_time = pendulum.from_timestamp(self.alert.start_time)
        self.start_time_label.time = start_time

        # Alert end time
        if self.alert.end_time is not None:
            end_time = pendulum.from_timestamp(self.alert.end_time)
            self.end_time_label.time = end_time
            self.end_time_label.setVisible(True)
        else:
            self.end_time_label.setHidden(True)

    def set_alert_verification(self, verification: Union[None, bool]):

        # Failsafe
        if not self.alert:
            return

        self._set_ui_verification(verification_override=verification)

        def handle_set_verification_error(error: api_errors.BaseAPIError):

            self._set_ui_verification()

            logging.warning("An error occurred while attempting to set alert "
                            "verification value on the BrainFrame server. "
                            "The value has been reverted on the client.")

            # Reset to the current stored state
            if isinstance(error, api_errors.AlertNotFoundError):
                # TODO: Delete entry? Wait for AlertLog to clean up?
                pass
            else:
                # Log an error
                logging.error(error)

        async_api_pubsub.set_alert_verification(
            thread_owner=self,
            alert=self.alert,
            verified_as=verification,
            on_error=handle_set_verification_error
        )

    def _set_ui_verification(self,
                             # -1 is a sentinel
                             verification_override: Union[None, bool] = -1):

        true_button = self.verified_true_button
        false_button = self.verified_false_button

        verify_true_message = self.tr("Verify alert")
        verify_false_message = self.tr("Mark alert as false positive")
        deverify_true_message = self.tr("Unverify alert")
        deverify_false_message = self.tr("Unmark alert as false positive")

        # -1 is a sentinel
        if verification_override == -1:
            verification = self.alert.verified_as
        else:
            verification = verification_override

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

    @pyqtSlot(QAbstractButton)
    def _alert_verified(self, button: TextIconButton):
        if button is self.verified_true_button and button.isChecked():
            new_verification = True
            # Clear the other button
            self.verified_false_button.setChecked(False)
        elif button is self.verified_false_button and button.isChecked():
            new_verification = False
            # Clear the other button
            self.verified_true_button.setChecked(False)
        else:
            new_verification = None

        self.set_alert_verification(new_verification)
