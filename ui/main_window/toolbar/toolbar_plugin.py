from ui.resources import BasePlugin


class Toolbar(BasePlugin):

    # noinspection PyUnresolvedReferences
    from .toolbar import Toolbar as Widget

    def __init__(self):

        super().__init__(self, self.Widget)
