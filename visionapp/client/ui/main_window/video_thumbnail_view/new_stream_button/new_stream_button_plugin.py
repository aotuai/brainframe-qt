from visionapp.client.ui.resources import BasePlugin


class NewStreamButton(BasePlugin):

    # noinspection PyUnresolvedReferences
    from visionapp.client.ui.main_window.video_thumbnail_view.new_stream_button \
        .new_stream_button import NewStreamButton as Widget

    def __init__(self):

        super().__init__(self.Widget)
