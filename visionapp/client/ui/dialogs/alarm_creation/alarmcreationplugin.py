from visionapp.client.ui.resources import BasePlugin


class AlarmCreationDialog(BasePlugin):

    # noinspection PyUnresolvedReferences
    from visionapp.client.ui.dialogs.alarm_creation.alarm_creation \
        import AlarmCreationDialog as Widget

    def __init__(self):

        super().__init__(self.Widget)
