from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget

from brainframe.client.ui.main_window.activities.stream_activity import \
    StreamActivity
from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.paths import image_paths, qt_qss_paths
from brainframe.client.ui.resources.ui_elements.containers import \
    StackedTabWidget


class MainWindowUI(QMainWindow):

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.tab_widget = self._init_tab_widget()
        self.stream_activity = self._init_stream_activity()

        self._init_layout()
        self._init_style()

    def _init_tab_widget(self) -> StackedTabWidget:
        tab_widget = StackedTabWidget(self)
        return tab_widget

    def _init_stream_activity(self) -> StreamActivity:
        stream_activity = StreamActivity(self)
        return stream_activity

    def _init_layout(self):
        self.setCentralWidget(self.tab_widget)

        stream_activity_icon = QIcon(str(image_paths.new_stream_icon))
        self.tab_widget.add_widget(self.stream_activity, "Streams",
                                   stream_activity_icon)

    def _init_style(self):
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.resize(1400, 900)

        stylesheet_watcher.watch(self, qt_qss_paths.main_window_qss)
