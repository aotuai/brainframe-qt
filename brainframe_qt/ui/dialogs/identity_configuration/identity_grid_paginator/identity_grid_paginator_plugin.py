from brainframe.client.ui.resources.qt_plugins.base_plugin import BasePlugin


class IdentityGridPaginator(BasePlugin):
    from brainframe.client.ui.dialogs.identity_configuration. \
        identity_grid_paginator.identity_grid_paginator \
        import IdentityGridPaginator as Widget

    def __init__(self):
        super().__init__(self.Widget)

    def isContainer(self):
        return True
