import typing

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout

from brainframe.client.ui.resources.mixins.layout import SortedLayoutMI
from .alert_log_entry import AlertLogEntry


class AlertLogLayoutUI(QVBoxLayout):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setSpacing(0)
        self.setAlignment(Qt.AlignTop)
        self.setContentsMargins(0, 0, 0, 0)


class AlertLogLayout(SortedLayoutMI, AlertLogLayoutUI):

    def _reversed(self):
        return True

    # noinspection PyMethodMayBeStatic
    def _sort_key(self, alert_log_entry: AlertLogEntry) -> int:
        return alert_log_entry.alert.id

    def take_widget_at(self, index: int) -> AlertLogEntry:
        return typing.cast(AlertLogEntry, self.takeAt(index).widget())

    def widget_at(self, index: int) -> AlertLogEntry:
        return typing.cast(AlertLogEntry, self.itemAt(index).widget())
