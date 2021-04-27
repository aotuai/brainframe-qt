from typing import Callable

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView, QWidget

from brainframe_qt.ui.resources import stylesheet_watcher
from brainframe_qt.ui.resources.config import ServerSettings
from brainframe_qt.ui.resources.paths import qt_qss_paths
from .stream_graphics_scene import StreamGraphicsScene


class StreamWidgetUI(QGraphicsView):
    # Type hint that self.scene() is more than just a QGraphicsScene
    scene: Callable[[], StreamGraphicsScene]

    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)

        self.render_config = ServerSettings()

        self._init_scene()
        self._init_style()

    def _init_scene(self) -> None:
        scene = StreamGraphicsScene(
            render_config=self.render_config,
            parent=self
        )

        self.setScene(scene)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.stream_widget_qss)

    def hasHeightForWidth(self):
        """Enable the use of heightForWidth"""
        return True

    def heightForWidth(self, width: int):
        """Lock the aspect ratio of the widget to match the aspect ratio of the
        scene and its video frame
        """
        if not self.scene().width():
            return 0

        return width * self.scene().height() / self.scene().width()
