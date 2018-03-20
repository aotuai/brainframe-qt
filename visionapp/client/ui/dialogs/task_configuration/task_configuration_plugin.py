from ui.resources import BasePlugin


class TaskConfiguration(BasePlugin):

    # noinspection PyUnresolvedReferences
    from ui.dialogs.task_configuration.task_configuration \
        import TaskConfiguration as Widget

    def __init__(self):

        super().__init__(self.Widget)
