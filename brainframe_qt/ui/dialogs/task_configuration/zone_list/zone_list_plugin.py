from brainframe.client.ui.resources.qt_plugins.base_plugin import BasePlugin


class ZoneList(BasePlugin):

    # noinspection PyUnresolvedReferences
    from brainframe.client.ui.dialogs.task_configuration.zone_list.zone_list \
        import ZoneList as Widget

    def __init__(self):

        super().__init__(self.Widget)
