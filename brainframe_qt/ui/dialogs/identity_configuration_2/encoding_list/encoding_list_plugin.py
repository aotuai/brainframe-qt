from brainframe.client.ui.resources import BasePlugin


class EncodingList(BasePlugin):
    from brainframe.client.ui.dialogs.identity_configuration_2.encoding_list \
        import EncodingList as Widget

    def __init__(self):
        super().__init__(self.Widget)
