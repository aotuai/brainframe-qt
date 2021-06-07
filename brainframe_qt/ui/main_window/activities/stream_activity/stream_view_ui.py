import functools

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QHBoxLayout, QSplitter, QWidget

from brainframe_qt.ui.main_window.video_expanded_view.video_expanded_view import \
    VideoExpandedView
from brainframe_qt.ui.main_window.video_thumbnail_view import VideoThumbnailView
from brainframe_qt.ui.resources import stylesheet_watcher
from brainframe_qt.ui.resources.paths import qt_qss_paths
from brainframe_qt.ui.resources.ui_elements.buttons import FloatingActionButton


class _StreamViewUI(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.video_thumbnail_view = self._init_video_thumbnail_view()
        self.new_stream_button = self._init_new_stream_button()
        self.splitter = self._init_splitter()
        self.video_expanded_view = self._init_video_expanded_view()

        self._init_layout()
        self._init_style()

    def _init_video_thumbnail_view(self) -> VideoThumbnailView:
        video_thumbnail_view = VideoThumbnailView(self)
        return video_thumbnail_view

    def _init_new_stream_button(self) -> FloatingActionButton:
        new_stream_button = FloatingActionButton(
            self.video_thumbnail_view,
            self.palette().highlight())

        new_stream_button.setToolTip(self.tr("Add new stream"))

        return new_stream_button

    def _init_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Horizontal, self)
        splitter.setChildrenCollapsible(False)
        return splitter

    def _init_video_expanded_view(self) -> VideoExpandedView:
        video_expanded_view = VideoExpandedView(self)
        video_expanded_view.hide()
        return video_expanded_view

    def _init_layout(self) -> None:
        layout = QHBoxLayout()

        layout.addWidget(self.splitter)
        self.splitter.addWidget(self.video_thumbnail_view)
        self.splitter.addWidget(self.video_expanded_view)

        # https://stackoverflow.com/a/43835396/8134178
        big_number = 1000000
        ratio = 4  # 1:4 ratio when expanded
        self.splitter.setSizes([big_number, ratio * big_number])

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.stream_view_qss)
