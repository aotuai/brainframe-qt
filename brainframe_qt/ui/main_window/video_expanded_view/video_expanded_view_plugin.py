from brainframe.client.ui.resources.qt_plugins.base_plugin import BasePlugin


class VideoExpandedView(BasePlugin):

    # noinspection PyUnresolvedReferences
    from brainframe.client.ui.main_window.video_expanded_view.video_expanded_view \
        import VideoExpandedView as Widget

    def __init__(self):

        super().__init__(self.Widget)
