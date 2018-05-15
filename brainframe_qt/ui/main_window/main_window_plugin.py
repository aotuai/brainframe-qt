from brainframe.client.ui.resources import BasePlugin


class MainWindow(BasePlugin):

    # noinspection PyUnresolvedReferences
    from brainframe.client.ui.main_window.main_window import MainWindow as Widget

    def __init__(self):

        super().__init__(self.Widget)