from PyQt5.QtCore import QMargins, Qt
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.mixins.style import TransientScrollbarMI
from brainframe.client.ui.resources.paths import qt_qss_paths


class AlarmViewUI(QScrollArea, TransientScrollbarMI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        container_widget = self._init_container_widget()
        self._init_viewport_widget()

        self.setWidget(container_widget)

        self._init_style()

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setWidgetResizable(True)

        stylesheet_watcher.watch(self, qt_qss_paths.alarm_view_qss)

    def _init_container_widget(self) -> QWidget:
        container_widget = QWidget(self)
        container_widget.setObjectName("container")
        container_widget.setAttribute(Qt.WA_StyledBackground, True)

        # Leave some space on the right for the scrollbar
        contents_margins: QMargins = self.contentsMargins()
        contents_margins.setLeft(50)
        contents_margins.setRight(50)
        container_widget.setContentsMargins(contents_margins)

        container_widget.setLayout(self._init_container_widget_layout())

        return container_widget

    # noinspection PyMethodMayBeStatic
    def _init_container_widget_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.setAlignment(Qt.AlignTop)
        return layout

    def _init_viewport_widget(self) -> None:
        # Give the viewport a name for the stylesheet
        self.viewport().setObjectName("viewport")
