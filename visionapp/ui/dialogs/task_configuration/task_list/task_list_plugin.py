from ui.resources import BasePlugin


class TaskList(BasePlugin):

    # noinspection PyUnresolvedReferences
    from ui.dialogs.task_configuration.task_list.task_list \
        import TaskList as Widget

    def __init__(self):

        super().__init__(self.Widget)
