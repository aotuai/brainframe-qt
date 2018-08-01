from brainframe.client.ui.resources import BasePlugin


class ThumbnailScrollArea(BasePlugin):

    from brainframe.client.ui.main_window.video_thumbnail_view.thumbnail_scroll_area. \
        thumbnail_scroll_area import ThumbnailScrollArea as Widget

    def __init__(self):

        super().__init__(self.Widget)
