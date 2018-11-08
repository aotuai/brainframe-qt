from .base_plugin_options import BasePluginOptionsWidget


class GlobalPluginOptionsWidget(BasePluginOptionsWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("Global Plugin Options")
        self.override_label.hide()

