from brainframe.client.ui.resources import BasePlugin


class IdentityInfo(BasePlugin):

    # noinspection PyUnresolvedReferences
    from brainframe.client.ui.dialogs.identity_configuration_2.identity_info \
        import IdentityInfo as Widget

    def __init__(self):

        super().__init__(self.Widget)
