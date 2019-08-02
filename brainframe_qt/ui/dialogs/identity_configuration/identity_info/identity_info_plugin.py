from brainframe.client.ui.resources.qt_plugins.base_plugin import BasePlugin


class IdentityInfo(BasePlugin):

    from brainframe.client.ui.dialogs.identity_configuration.identity_info \
        import IdentityInfo as Widget

    def __init__(self):

        super().__init__(self.Widget)
