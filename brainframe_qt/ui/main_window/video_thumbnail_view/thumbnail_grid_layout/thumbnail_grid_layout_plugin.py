from brainframe.client.ui.resources import BasePlugin


class ThumbnailGridLayout(BasePlugin):

    from brainframe.client.ui.main_window.video_thumbnail_view.thumbnail_grid_layout.thumbnail_grid_layout import ThumbnailGridLayout as Widget

    def __init__(self):

        super().__init__(self.Widget)
