from brainframe.client.ui.resources.qt_plugins.base_plugin import BasePlugin


class PluginList(BasePlugin):
    # noinspection PyUnresolvedReferences
    from brainframe.client.ui.dialogs.capsule_configuration.plugin_list.plugin_list import \
        PluginList as Widget

    def __init__(self):
        super().__init__(self.Widget)
