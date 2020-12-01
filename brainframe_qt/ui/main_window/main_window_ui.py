from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QWidget

from brainframe_qt.ui.main_window.toolbar import MainToolbar
from brainframe_qt.ui.resources import stylesheet_watcher
from brainframe_qt.ui.resources.paths import qt_qss_paths
from brainframe_qt.ui.resources.ui_elements.containers import \
    SidebarDockWidget


class MainWindowUI(QMainWindow):

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.stacked_widget = self._init_tab_widget()
        self.toolbar = self._init_toolbar()

        self.sidebar_dock_widget = self._init_sidebar_dock_widget()

        self._init_layout()
        self._init_style()

    def _init_tab_widget(self) -> QStackedWidget:
        tab_widget = QStackedWidget(self)
        return tab_widget

    def _init_toolbar(self) -> MainToolbar:
        toolbar = MainToolbar(self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        return toolbar

    def _init_sidebar_dock_widget(self) -> SidebarDockWidget:
        sidebar_dock_widget = SidebarDockWidget(self)
        return sidebar_dock_widget

    def _init_layout(self) -> None:
        self.setCentralWidget(self.stacked_widget)

        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

        self.addDockWidget(Qt.RightDockWidgetArea, self.sidebar_dock_widget)
        self.sidebar_dock_widget.hide()

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.resize(1400, 900)

        stylesheet_watcher.watch(self, qt_qss_paths.main_window_qss)
