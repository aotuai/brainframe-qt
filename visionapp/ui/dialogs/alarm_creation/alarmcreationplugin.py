from ui.resources import BasePlugin


class AlarmCreationDialog(BasePlugin):

    # noinspection PyUnresolvedReferences
    from ui.dialogs.alarm_creation.alarm_creation \
        import AlarmCreationDialog as Widget

    def __init__(self):

        super().__init__(self.Widget)
