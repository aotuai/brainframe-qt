from PyQt5.QtCore import QMargins, Qt
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.mixins.style import TransientScrollbarMI
from brainframe.client.ui.resources.paths import qt_qss_paths
from brainframe.client.ui.resources.ui_elements.widgets import \
    BackgroundImageText


class AlarmViewUI(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.background_widget = self._init_background_widget()
        self.container_widget = self._init_container_widget()
        self.scroll_area = self._init_scroll_area()

        self._init_layout()
        self._init_style()

    def _init_background_widget(self) -> BackgroundImageText:
        text = self.tr("No streams are being analyzed right now, so there is "
                       "nothing to show here")
        svg_path = ":/icons/alert"

        background_widget = BackgroundImageText(text, svg_path, self)

        return background_widget

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

    def _init_scroll_area(self) -> "_AlarmViewScrollArea":
        scroll_area = _AlarmViewScrollArea(self)

        scroll_area.setWidget(self.container_widget)

        return scroll_area

    def _init_layout(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.background_widget)
        layout.addWidget(self.scroll_area)

        self.scroll_area.setHidden(True)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alarm_view_qss)


class _AlarmViewScrollArea(QScrollArea, TransientScrollbarMI):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._init_viewport_widget()

        self._init_style()

    def _init_viewport_widget(self) -> None:
        # Give the viewport a name for the stylesheet
        self.viewport().setObjectName("viewport")

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setWidgetResizable(True)
