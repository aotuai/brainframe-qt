from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDockWidget, QWidget

from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.paths import qt_qss_paths


class _SidebarDockWidgetUI(QDockWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_style()

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.sidebar_dock_widget_qss)


class SidebarDockWidget(_SidebarDockWidgetUI):
    closed = pyqtSignal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.closed.emit()
        super().closeEvent(event)
