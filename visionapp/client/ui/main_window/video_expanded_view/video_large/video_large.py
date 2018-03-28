from visionapp.client.ui.resources.stream_widget import StreamWidget


class VideoLarge(StreamWidget):

    def __init__(self, parent=None, stream_conf=None, frame_rate=30):

        super().__init__(stream_conf, frame_rate, parent)
