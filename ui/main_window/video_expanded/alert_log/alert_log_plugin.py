from ui.resources import BasePlugin


class AlertLog(BasePlugin):

    # noinspection PyUnresolvedReferences
    from alert_log import AlertLog as Widget

    def __init__(self):

        super().__init__(self.Widget)
