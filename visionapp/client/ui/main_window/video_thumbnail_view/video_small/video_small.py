from PyQt5.QtCore import pyqtSignal, pyqtSlot

from ui.resources.stream_widget import StreamWidget


class VideoSmall(StreamWidget):
    """Video for ThumbnailView"""

    stream_clicked = pyqtSignal(int)

    def __init__(self, parent=None, stream_conf=None, frame_rate=30):
        super().__init__(stream_conf, frame_rate, parent)

        self.parent = parent

        # Because these widgets are added dynamically, we can't connect slots
        # and signals using QtDesigner and have to do it manually
        if parent is not None:  # Required or QtDesigner throws errors
            self.stream_clicked.connect(parent.thumbnail_stream_clicked_slot)
            parent.remove_selection_border_signal.connect(
                self.remove_selection_border_slot)

    def mouseReleaseEvent(self, event):

        print("Moused button released")

        # Add border around stream to indicate its selection
        self.add_selection_border()

        self.stream_clicked.emit(self.stream_id)

        super().mousePressEvent(event)

    def add_selection_border(self):
        """Add border around stream"""
        pass

    @pyqtSlot(int)
    def remove_selection_border_slot(self, stream_id):
        """Remove border around stream if stream_id matches self.id"""
        if self.stream_id == stream_id:
            # TODO: Remove border
            pass