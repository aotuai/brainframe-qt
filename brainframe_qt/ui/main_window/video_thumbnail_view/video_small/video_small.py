from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QSizePolicy

from brainframe.client.ui.resources.video_items.stream_widget import StreamWidget


class VideoSmall(StreamWidget):
    """Video for ThumbnailView"""

    stream_clicked = pyqtSignal(int)

    def __init__(self, parent=None, stream_conf=None, frame_rate=30):
        super().__init__(stream_conf, frame_rate, parent=parent)

        # Because these widgets are added dynamically, we can't connect slots
        # and signals using QtDesigner and have to do it manually
        if parent is not None:  # Required or QtDesigner throws errors
            # noinspection PyUnresolvedReferences
            # .connect is erroneously detected as unresolved
            self.stream_clicked.connect(parent.thumbnail_stream_clicked_slot)

        # self.setStyleSheet("background-color:#404040;")

    def mouseReleaseEvent(self, event):
        # Add border around stream to indicate its selection
        self.add_selection_border()

        self.stream_clicked.emit(self.stream_conf.id)

        super().mousePressEvent(event)

    def add_selection_border(self):
        """Add border around stream"""
        pass

    def remove_selection_border(self):
        """Remove border around stream"""
        pass

    def _resize(self, size):
        """Resize widget to max allowed height that maintains aspect ratio"""
        super()._resize(size)

        if not self.scene().width():
            return

        aspect_ratio = self.scene().height() / self.scene().width()
        height = int(size.width() * aspect_ratio)
        self.setFixedHeight(height)
