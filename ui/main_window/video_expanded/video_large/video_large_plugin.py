from ui.resources import BasePlugin


class VideoLarge(BasePlugin):

    # noinspection PyUnresolvedReferences
    from .video_large import VideoLarge as Widget

    def __init__(self):

        super().__init__(self, self.Widget)
