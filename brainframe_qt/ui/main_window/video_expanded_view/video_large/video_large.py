from PyQt5.QtWidgets import QSizePolicy, QWidget

from brainframe.client.ui.resources.video_items.streams import StreamWidget


class VideoLarge(StreamWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)

        # I was under the impression that this was the default size policy, but
        # removing it prevents the alert log from expanding into more than half
        # of the layout when the VideoLarge widget is very narrow
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
