from ui.resources import BasePlugin


class VideoLarge(BasePlugin):

    # noinspection PyUnresolvedReferences
    from ui.main_window.video_expanded_view.video_large.video_large \
        import VideoLarge as Widget

    def __init__(self):

        super().__init__(self.Widget)
