from PyQt5.QtGui import QColor

from brainframe_qt.ui.resources.video_items.base import CircleItem, VideoItem


class DraggableVertex(CircleItem):
    # TODO: Tie to size of scene
    DEFAULT_RADIUS = 10
    DEFAULT_BORDER_THICKNESS = 5
    DEFAULT_COLOR = QColor(200, 50, 50)

    def __init__(self, position: VideoItem.PointType, *, parent: VideoItem):
        super().__init__(position, color=self.DEFAULT_COLOR,
                         radius=self.DEFAULT_RADIUS,
                         border_thickness=self.DEFAULT_BORDER_THICKNESS,
                         parent=parent)
