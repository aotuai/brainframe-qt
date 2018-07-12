from brainframe.client.ui.resources import BaseContainerPlugin


class ThumbnailGridContainer(BaseContainerPlugin):
    from brainframe.client.ui.main_window.video_thumbnail_view.thumbnail_grid_container.thumbnail_grid_container import \
        ThumbnailGridContainer as Widget

    def __init__(self):
        super().__init__(self.Widget)
