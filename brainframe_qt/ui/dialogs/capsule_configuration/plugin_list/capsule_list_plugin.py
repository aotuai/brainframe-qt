from brainframe.client.ui.resources.qt_plugins.base_plugin import BasePlugin


class CapsuleList(BasePlugin):
    # noinspection PyUnresolvedReferences
    from brainframe.client.ui.dialogs.capsule_configuration.plugin_list.capsule_list import \
        CapsuleList as Widget

    def __init__(self):
        super().__init__(self.Widget)
