from brainframe.client.ui.resources.qt_plugins.base_plugin import BasePlugin


class EncodingList(BasePlugin):
    from brainframe.client.ui.main_window.activities.identity_configuration.encoding_list \
        import EncodingList as Widget

    def __init__(self):
        super().__init__(self.Widget)
