from visionapp.client.ui.resources import BasePlugin


class VideoSmall(BasePlugin):

    # noinspection PyUnresolvedReferences
    from visionapp.client.ui.main_window.video_thumbnail_view.video_small.video_small \
        import VideoSmall as Widget

    def __init__(self):

        super().__init__(self.Widget)
