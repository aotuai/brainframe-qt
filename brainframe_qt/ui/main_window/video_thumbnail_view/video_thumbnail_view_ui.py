from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from brainframe_qt.ui.resources import stylesheet_watcher
from brainframe_qt.ui.resources.mixins.style import TransientScrollbarMI
from brainframe_qt.ui.resources.paths import qt_qss_paths
from brainframe_qt.ui.resources.ui_elements.widgets import BackgroundImageText

from .widgets.thumbnail_grid_layout import ThumbnailGridLayout


class _VideoThumbnailViewUI(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.background_widget = self._init_background_widget()

        self.alert_stream_layout = self._init_alert_stream_layout()
        self.alertless_stream_layout = self._init_alertless_stream_layout()

        self.container_widget = self._init_container_widget()
        self.scroll_area = self._init_scroll_area()

        self._init_layout()
        self._init_style()

    def _init_background_widget(self) -> BackgroundImageText:
        text = self.trUtf8("Click the ➕ button to add a new stream".encode(encoding='UTF-8'))
        svg_path = ":/icons/no_streams"

        background_widget = BackgroundImageText(text, svg_path, self)

        return background_widget

    def _init_container_widget(self) -> QWidget:
        container_widget = QWidget(self)
        container_widget.setObjectName("container")
        container_widget.setAttribute(Qt.WA_StyledBackground, True)

        container_widget.setLayout(self._init_container_widget_layout())

        container_widget.setAttribute(Qt.WA_StyledBackground, True)

        return container_widget

    # noinspection PyMethodMayBeStatic
    def _init_container_widget_layout(self) -> QVBoxLayout:
        layout = _ContainerLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.alert_stream_layout)
        layout.addWidget(self.alertless_stream_layout)

        layout.setAlignment(self.alert_stream_layout, Qt.AlignTop)
        layout.setAlignment(self.alertless_stream_layout, Qt.AlignTop)

        return layout

    def _init_scroll_area(self) -> "_ThumbnailScrollArea":
        scroll_area = _ThumbnailScrollArea(self)

        scroll_area.setWidget(self.container_widget)

        return scroll_area

    def _init_alert_stream_layout(self) -> ThumbnailGridLayout:
        alert_stream_layout = ThumbnailGridLayout(self)

        layout_name = self.tr("Streams with ongoing alerts:")
        alert_stream_layout.layout_name = layout_name

        alert_stream_layout.expand_grid(True)

        return alert_stream_layout

    def _init_alertless_stream_layout(self) -> ThumbnailGridLayout:
        alertless_stream_layout = ThumbnailGridLayout(self)

        layout_name = self.tr("Streams without alerts:")
        alertless_stream_layout.layout_name = layout_name

        alertless_stream_layout.expand_grid(True)

        return alertless_stream_layout

    def _init_layout(self) -> None:
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(self.background_widget)
        layout.addWidget(self.scroll_area)

        self.scroll_area.hide()

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.video_thumbnail_view_qss)


class _ThumbnailScrollArea(QScrollArea, TransientScrollbarMI):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._init_viewport_widget()

        self._init_style()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Prevent the scroll area from scrolling horizontally by setting
        minimumWidth to be the sizeHint of its contents"""
        super().resizeEvent(event)
        self.setMinimumWidth(self.widget().minimumSizeHint().width())

    def _init_viewport_widget(self) -> None:
        # Give the viewport a name for the stylesheet
        self.viewport().setObjectName("viewport")
        self.viewport().setAttribute(Qt.WA_StyledBackground, True)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setWidgetResizable(True)


class _ContainerLayout(QVBoxLayout):

    def sizeHint(self) -> QSize:
        """This is a hack. Not doing this makes the ThumbnailGridLayouts get
        squished vertically, when used in conjunction with their container
        layout's alignment set to Qt.AlignTop. I don't know why this fixes it
        """
        sh = super().sizeHint()
        sh.setHeight(9999999)
        return sh
