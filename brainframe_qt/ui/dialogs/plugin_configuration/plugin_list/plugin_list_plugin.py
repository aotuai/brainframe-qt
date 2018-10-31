from brainframe.client.ui.resources import BasePlugin


class PluginList(BasePlugin):
    # noinspection PyUnresolvedReferences
    from brainframe.client.ui.dialogs.plugin_configuration.plugin_list.plugin_list import \
        PluginList as Widget

    def __init__(self):
        super().__init__(self.Widget)
