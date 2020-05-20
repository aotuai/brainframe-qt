from .base_plugin_options import BaseCapsuleOptionsWidget

from brainframe.client.api import api


class StreamCapsuleOptionsWidget(BaseCapsuleOptionsWidget):
    def __init__(self, stream_id, parent=None):
        super().__init__(parent=parent)
        assert stream_id is not None
        self.window().setWindowTitle(self.tr("Stream Plugin Options"))
        self.stream_id = stream_id

    def change_plugin(self, plugin_name):
        # Add all of the global options
        super().change_plugin(plugin_name)

        # Get stream-specific option items
        stream_options = api.get_plugin_option_vals(plugin_name,
                                                    self.stream_id)
        enabled_option = api.is_plugin_active(plugin_name, self.stream_id)

        # Lock all options that are not overwritten by stream specific options
        for option_item in self.option_items:
            is_locked = option_item.option_name not in stream_options.keys()
            option_item.show_lock(True)
            option_item.set_locked(is_locked)

        # Set the state for other generic options
        self.enabled_option.show_lock(True)
        self.enabled_option.set_locked(enabled_option is None)
        # Set the stream-specific setting, if there is one
        if enabled_option is not None:
            self.enabled_option.set_val(enabled_option)

        for option_name, option_patch in stream_options.items():
            option_item = next(o for o in self.option_items
                               if o.option_name == option_name)
            option_item.set_val(option_patch)

    def apply_changes(self, stream_id=None):
        super().apply_changes(stream_id=self.stream_id)
