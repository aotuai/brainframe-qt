from brainframe.client.ui.resources import BasePlugin


class VideoExpandedView(BasePlugin):
    from brainframe.client.ui.dialogs.identity_configuration. \
        identity_grid_paginator.identity_grid.identity_grid \
        import IdentityGrid as Widget

    def __init__(self):
        super().__init__(self.Widget)
