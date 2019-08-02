from brainframe.client.ui.resources.qt_plugins.base_plugin import BasePlugin


class VideoExpandedView(BasePlugin):
    from brainframe.client.ui.dialogs.identity_configuration. \
        identity_search_filter.identity_search_filter \
        import IdentitySearchFilter as Widget

    def __init__(self):
        super().__init__(self.Widget)
