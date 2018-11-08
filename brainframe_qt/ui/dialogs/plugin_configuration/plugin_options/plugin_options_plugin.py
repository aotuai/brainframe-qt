from brainframe.client.ui.resources import BasePlugin


class PluginOptions(BasePlugin):
    # noinspection PyUnresolvedReferences
    from brainframe.client.ui.dialogs.plugin_configuration.plugin_options.\
        base_plugin_options import BasePluginOptionsWidget as Widget

    def __init__(self):
        super().__init__(self.Widget)
