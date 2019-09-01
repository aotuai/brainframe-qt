from brainframe.client.ui.resources.qt_plugins.base_plugin import BasePlugin


class MainWindow(BasePlugin):

    # noinspection PyUnresolvedReferences
    from brainframe.client.ui.dialogs.identity_configuration.\
        identity_error_popup.tree_widget.tree_widget import TreeWidget as Widget

    def __init__(self):

        super().__init__(self.Widget)
