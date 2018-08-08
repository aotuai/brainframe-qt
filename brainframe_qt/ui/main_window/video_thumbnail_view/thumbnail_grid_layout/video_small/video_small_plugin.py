from brainframe.client.ui.resources import BasePlugin


class VideoSmall(BasePlugin):

    from brainframe.client.ui.main_window.video_thumbnail_view.thumbnail_grid_layout.video_small.video_small \
        import VideoSmall as Widget

    def __init__(self):

        super().__init__(self.Widget)
