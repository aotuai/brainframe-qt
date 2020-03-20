from typing import List, Optional, overload
import typing

from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from brainframe.client.api.codecs import Alert
from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.mixins.mouse import ClickableMI
from brainframe.client.ui.resources.mixins.style import TransientScrollbarMI
from brainframe.client.ui.resources.paths import qt_qss_paths
from .alert_log_entry import AlertLogEntry


class AlertLogUI(QScrollArea, TransientScrollbarMI):

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
            widget = self.widget().layout().itemAt(index).widget()
            return typing.cast(AlertLogEntry, widget)
        else:
            raise TypeError

    def add_alert(self, alert: Alert):
        alert_log_entry = AlertLogEntry(alert, self)
        self.widget().layout().addWidget(alert_log_entry)

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

        self.alert_log_entries.append(alert_log_entry)
