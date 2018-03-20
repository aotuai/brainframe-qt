from ui.resources.stream_widget import StreamWidget


class VideoLarge(StreamWidget):

    def __init__(self, parent=None, frame_rate=30):

        super().__init__(frame_rate, parent)
