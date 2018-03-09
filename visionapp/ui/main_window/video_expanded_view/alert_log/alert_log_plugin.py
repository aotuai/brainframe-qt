from ui.resources import BasePlugin


class AlertLog(BasePlugin):

    # noinspection PyUnresolvedReferences
    from ui.main_window.video_expanded_view.alert_log.alert_log \
        import AlertLog as Widget

    def __init__(self):

        super().__init__(self.Widget)
