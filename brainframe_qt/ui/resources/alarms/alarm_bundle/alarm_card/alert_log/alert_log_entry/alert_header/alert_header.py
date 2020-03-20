import logging
from typing import Union

import pendulum
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QAbstractButton, QButtonGroup, QFrame, \
    QHBoxLayout, QLabel, QSizePolicy, QWidget

from brainframe.client.api import api, api_errors
from brainframe.client.api.codecs import Alert
from brainframe.client.ui.resources import QTAsyncWorker, stylesheet_watcher
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

        self.verification_button_group.addButton(verified_true_button)

        return verified_true_button

    def _init_verified_false_button(self) -> TextIconButton:
        verified_false_button = TextIconButton("❌", self)
        verified_false_button.setObjectName("verified_false_button")

        verified_false_button.setFlat(True)
        verified_false_button.setCheckable(True)

        self.verification_button_group.addButton(verified_false_button)

        return verified_false_button


class AlertHeader(AlertHeaderUI, ClickableMI):
    alert_verified = pyqtSignal([int, type(None)], [int, bool])

    def __init__(self, alert: Alert, parent: QWidget):
        super().__init__(parent)

        self.alert = alert
        self.timezone = "America/Los_Angeles"

        self._init_signals()

        self._populate_alert_info()

    def _init_signals(self):
        self.verification_button_group.buttonClicked.connect(
            self._alert_verified)

    def open_alert_info_dialog(self):
        print(f"Opening dialog for {self.alert}")
        ...

    def _populate_alert_info(self) -> None:
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

        # Alert verification
        self._set_ui_verification(self.alert.verified_as)

    def set_alert_verification(self, verification: Union[None, bool]):
        self._set_ui_verification(verification)

        def handle_set_verification_success(_):
            print("Alert verified properly", verification)
            self.alert.verified_as = verification

            if verification is None:
                verified_signal = self.alert_verified[int, type(None)]
            else:
                verified_signal = self.alert_verified[int, bool]
            verified_signal.emit(self.alert.id, verification)

        def handle_set_verification_error(error: api_errors.BaseAPIError):

            logging.warning("An error occurred while attempting to set alert "
                            "verification value on the BrainFrame server. "
                            "The value has been reverted on the client.")

            # Reset to the current stored state
            self._populate_alert_info()
            if isinstance(error, api_errors.AlertNotFoundError):
                # Delete entry? Wait for AlertLog to clean up?
                raise error
            else:
                logging.error(error)

        QTAsyncWorker(self, api.set_alert_verification,
                      f_args=(self.alert.id,),
                      f_kwargs={"verified_as": verification},
                      on_success=handle_set_verification_success,
                      on_error=handle_set_verification_error) \
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