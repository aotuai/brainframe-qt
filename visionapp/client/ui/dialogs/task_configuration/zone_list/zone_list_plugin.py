from ui.resources import BasePlugin


class RegionList(BasePlugin):

    # noinspection PyUnresolvedReferences
    from ui.dialogs.task_configuration.zone_list.zone_list \
        import ZoneList as Widget

    def __init__(self):

        super().__init__(self.Widget)
