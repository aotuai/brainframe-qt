from .base_plugin_options import BasePluginOptionsWidget


class StreamPluginOptionsWidget(BasePluginOptionsWidget):
    def __init__(self, stream_id, parent=None):
        super().__init__(parent=parent)
        self.setTitle("Stream Plugin Options")
