from ui.resources import BasePlugin


class Toolbar(BasePlugin):

    # noinspection PyUnresolvedReferences
    from ui.main_window.toolbar.toolbar import Toolbar as Widget

    def __init__(self):

        super().__init__(self.Widget)
