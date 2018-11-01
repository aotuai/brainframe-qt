from brainframe.client.ui.resources import BasePlugin


class PluginOptions(BasePlugin):
    # noinspection PyUnresolvedReferences
    from brainframe.client.ui.dialogs.plugin_configuration.plugin_options.\
        plugin_options import PluginOptionsWidget as Widget

    def __init__(self):
        super().__init__(self.Widget)
