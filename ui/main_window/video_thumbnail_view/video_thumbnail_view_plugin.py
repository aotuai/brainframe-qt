from ui.resources import BasePlugin


class VideoThumbnailView(BasePlugin):

    # noinspection PyUnresolvedReferences
    from video_thumbnail_view import VideoThumbnailView as Widget

    def __init__(self):

        super().__init__(self.Widget)
