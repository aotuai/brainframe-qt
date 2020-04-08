from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QSplitter, QVBoxLayout, QWidget

from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.paths import qt_qss_paths
from brainframe.client.ui.resources.ui_elements.buttons import \
    FloatingActionButton
from .video_expanded_view.video_expanded_view import VideoExpandedView
from .video_thumbnail_view import VideoThumbnailView


class MainWindowUI(QMainWindow):

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._init_central_widget()
        self.splitter = self._init_splitter()
        self.video_thumbnail_view = self._init_video_thumbnail_view()
        self.new_stream_button = self._init_new_stream_button()
        self.video_expanded_view = self._init_video_expanded_view()

        self._init_layout()
        self._init_style()

    def _init_central_widget(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

    def _init_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Horizontal, self)
        splitter.setChildrenCollapsible(False)
        return splitter

    def _init_video_thumbnail_view(self) -> VideoThumbnailView:
        video_thumbnail_view = VideoThumbnailView(self)
        return video_thumbnail_view

    def _init_video_expanded_view(self) -> VideoExpandedView:
        video_expanded_view = VideoExpandedView(self)
        video_expanded_view.setHidden(True)
        return video_expanded_view

    def _init_new_stream_button(self) -> FloatingActionButton:
        new_stream_button = FloatingActionButton(
            self.video_thumbnail_view,
            self.palette().highlight())

        new_stream_button.setToolTip(self.tr("Add new stream"))

        return new_stream_button

    def _init_layout(self):
        layout = QVBoxLayout()

        layout.addWidget(self.splitter)
        self.splitter.addWidget(self.video_thumbnail_view)
        self.splitter.addWidget(self.video_expanded_view)

        self.centralWidget().setLayout(layout)

    def _init_style(self):
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.resize(1400, 900)

        stylesheet_watcher.watch(self, qt_qss_paths.main_window_qss)
