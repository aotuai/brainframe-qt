from ui.resources import BasePlugin


class StreamConfiguration(BasePlugin):

    # noinspection PyUnresolvedReferences
    from ui.dialogs.stream_configuration.stream_configuration \
        import StreamConfiguration as Widget

    def __init__(self):

        super().__init__(self.Widget)
