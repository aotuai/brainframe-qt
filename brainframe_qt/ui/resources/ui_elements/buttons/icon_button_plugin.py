from brainframe.client.ui.resources.qt_plugins.base_plugin import BasePlugin


class TextIconButton(BasePlugin):
    from brainframe.client.ui.resources.ui_elements.buttons \
        import TextIconButton as Widget

    def __init__(self):
        super().__init__(self.Widget)
