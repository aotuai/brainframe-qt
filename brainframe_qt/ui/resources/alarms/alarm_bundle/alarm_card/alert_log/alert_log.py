from typing import Optional
import typing

from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QScrollArea, QWidget

from brainframe.api.codecs import Alert
from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.mixins.mouse import ClickableMI
from brainframe.client.ui.resources.mixins.style import TransientScrollbarMI
from brainframe.client.ui.resources.paths import qt_qss_paths
from .alert_log_entry import AlertLogEntry
from .alert_log_layout import AlertLogLayout


class AlertLogUI(QScrollArea, TransientScrollbarMI):

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)

        # Initialize widgets
        self.container_layout = self._init_container_layout()
        container_widget = self._init_container_widget()
        self.setWidget(container_widget)

        self._init_viewport_widget()

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

        container_widget.setLayout(self.container_layout)

        return container_widget

    # noinspection PyMethodMayBeStatic
    def _init_container_layout(self) -> AlertLogLayout:
        layout = AlertLogLayout()
        return layout

    def _init_viewport_widget(self) -> None:
        # Give the viewport a name for the stylesheet
        self.viewport().setObjectName("viewport")


class AlertLog(AlertLogUI, ClickableMI):

    alert_activity_changed = pyqtSignal(bool)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.max_alerts = None
        self._alert_active = typing.cast(bool, None)

    def add_alert(self, alert: Alert):
        alert_log_entry = AlertLogEntry(alert, self)

        # Add widget to the top of the layout
        layout = typing.cast(AlertLogLayout, self.widget().layout())
        layout.addWidget(alert_log_entry)

        # When an AlertLogEntry is expanded, make sure it and its contents are
        # visible in the ScrollArea
        alert_log_entry.expansion_changed.connect(
            self._ensure_alert_log_entry_visible)
        alert_log_entry.alert_activity_changed.connect(
            self._interpret_alert_activity_changed)

        # Ok sooo...
        # Adding a widget to a layout calls QLayout.addChildWidget. This calls
        # AlertLogEntry.setVisible but using QMetaObject.invokeMethod.
        # This means that AlertLogEntry.setVisible is only called in the _next_
        # Event Loop. QWidget.setVisible is where size recalculation is
        # performed. We _must_ call updateGeometry after our sizeHint changes.
        # Therefore, I update the geometry using a singleshot, which adds it to
        # the Event Loop queue and should be performed after the widget has
        # been set visible (i.e. size is recalculated)
        QTimer.singleShot(0, self.updateGeometry)

        if self.max_alerts is not None \
                and self.container_layout.count() > self.max_alerts:
            self.pop_alert()

        # This check to ensure edge case where self.max_alerts = 0 doesn't
        # break anything
        if self.container_layout.count() == 0:
            latest_alert_active = False
        else:
            latest_alert = self.container_layout.widget_at(0)
            latest_alert_active = (latest_alert.alert.end_time is None)

        if self._alert_active != latest_alert_active:
            self._alert_active = latest_alert_active
            self.alert_activity_changed.emit(latest_alert_active)

    def pop_alert(self):
        last_index = self.container_layout.count() - 1
        alert_log_entry = self.container_layout.take_widget_at(last_index)

        alert_log_entry.expansion_changed.disconnect()

        # Add widget to the top of the layout
        alert_log_entry.deleteLater()

        QTimer.singleShot(0, self.updateGeometry)

        if self.container_layout.count() == 0 and self._alert_active:
            self._alert_active = False
            self.alert_activity_changed.emit(False)

    def _ensure_alert_log_entry_visible(self, expanded: bool):

        if not expanded:
            return

        alert_log_entry = typing.cast(AlertLogEntry, self.sender())

        # https://stackoverflow.com/a/52450450/8134178
        QTimer.singleShot(0, lambda: self.ensureWidgetVisible(alert_log_entry))

    def contains_alert(self, alert: Alert):
        for index in range(self.container_layout.count()):
            alert_log_entry = self.container_layout.widget_at(index)
            if alert_log_entry.alert.id == alert.id:
                return True
        return False

    @pyqtSlot(bool)
    def _interpret_alert_activity_changed(self, alert_active: bool):
        if self.container_layout.count() == 0 \
                or self.sender() != self.container_layout.widget_at(0):
            return

        if self._alert_active != alert_active:
            self._alert_active = alert_active
            self.alert_activity_changed.emit(alert_active)
