from ui.resources import BasePlugin


class VideoThumbnailView(BasePlugin):

    # noinspection PyUnresolvedReferences
    from ui.main_window.video_thumbnail_view.video_thumbnail_view \
        import VideoThumbnailView as Widget

    def __init__(self):

        super().__init__(self.Widget)
