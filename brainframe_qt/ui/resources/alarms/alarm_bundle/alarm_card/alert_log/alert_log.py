from typing import List, Optional, overload

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from brainframe.client.api.codecs import Alert
from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.mixins.mouse import ClickableMI
from brainframe.client.ui.resources.paths import qt_qss_paths
from .alert_log_entry import AlertLogEntry


class AlertLogUI(QScrollArea):

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)

        # Initialize widgets
        container_widget = self._init_container_widget()
        self._init_viewport_widget()

        self.setWidget(container_widget)

        self._init_style()

    def sizeHint(self):
        return self.widget().sizeHint()

    def minimumSizeHint(self):
        """The default QAbstractScrollArea implementation wants to leave room
        for scrollbars... we don't care about them vertically"""
        size_hint: QSize = super().minimumSizeHint()
        size_hint.setHeight(0)
        return size_hint

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setWidgetResizable(True)

        stylesheet_watcher.watch(self, qt_qss_paths.alert_log_qss)

    def _init_container_widget(self) -> QWidget:
        container_widget = QWidget(self)
        container_widget.setObjectName("container")
        container_widget.setAttribute(Qt.WA_StyledBackground, True)

        container_widget.setLayout(self._init_container_widget_layout())

        return container_widget

    # noinspection PyMethodMayBeStatic
    def _init_container_widget_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        return layout

    def _init_viewport_widget(self) -> None:
        # Give the viewport a name for the stylesheet
        self.viewport().setObjectName("viewport")


class AlertLog(AlertLogUI, ClickableMI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.alert_log_entries: List[AlertLogEntry] = []

    @overload
    def __getitem__(self, index: int) -> AlertLogEntry:
        """Returns the AlertLogEntry that at the supplied index"""
        ...

    @overload
    def __getitem__(self, alert: Alert) -> AlertLogEntry:
        """Returns the AlertLogEntry that corresponds to the supplied alert"""
        ...

    def __getitem__(self, key) -> AlertLogEntry:
        """Returns the AlertLogEntry for the given key"""
        if isinstance(key, Alert):
            alert = key
            search = (alert_log_entry for alert_log_entry in self
                      if alert_log_entry.alert.id == alert.id)
            try:
                return next(search)
            except StopIteration as exc:
                raise KeyError from exc
        elif isinstance(key, int):
            index = key
            return self.widget().layout().itemAt(index).widget()
        else:
            raise TypeError

    def add_alert(self, alert: Alert):
        alert_log_entry = AlertLogEntry(alert, self)

        self.widget().layout().addWidget(alert_log_entry)
        self.alert_log_entries.append(alert_log_entry)

        # This is a hack to get the layout to be properly sized.
        # Without this, at the end of this current event loop cycle,
        # The AlarmCard's size and sizeHint will be smaller than the AlertLog's
        # size hint. Calling .updateGeometry _now_ has no effect. Calling it in
        # a later event loop works fine.
        #
        # Note that
        #     alert_log_entry.setAttribute(Qt.WA_WState_Hidden, False)
        # inside .setVisible is what triggers this, but I still don't know why
        alert_log_entry.setVisible(True)
