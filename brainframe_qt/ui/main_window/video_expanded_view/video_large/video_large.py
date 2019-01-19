from PyQt5.QtWidgets import QSizePolicy

from brainframe.client.ui.resources.video_items.stream_widget_nouveau import (
    StreamWidget
)


class VideoLarge(StreamWidget):

    def __init__(self, parent=None, stream_conf=None):
        super().__init__(stream_conf, parent)

        # I was under the impression that this was the default size policy, but
        # removing it prevents the alert log from expanding into more than half
        # of the layout when the VideoLarge widget is very narrow
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
