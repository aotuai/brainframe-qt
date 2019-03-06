from PyQt5.QtWidgets import QPushButton, QGridLayout, QMessageBox

from brainframe.client.api import api

from .base_plugin_options import BasePluginOptionsWidget


class GlobalPluginOptionsWidget(BasePluginOptionsWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setTitle("Global Plugin Options")
        self.override_label.hide()

        self._reset_overriding_btn = QPushButton("Reset All Overriding Streams",
                                                 parent=self)
        self._reset_to_defaults_btn = QPushButton("Reset to Defaults",
                                                  parent=self)
        # Add the button to the buttons grid
        self.buttons_grid.addWidget(self._reset_to_defaults_btn, 0, 1)
        self.buttons_grid.addWidget(self._reset_overriding_btn, 1, 1)

        # Link buttons to functions
        self._reset_to_defaults_btn.clicked.connect(
            self.on_reset_to_defaults)
        self._reset_overriding_btn.clicked.connect(
            self.on_reset_overriding_streams)

    def on_reset_to_defaults(self):
        """
        Reset all values to default after prompting the user

        Connected to:
        - QPushButton -- Dynamic
          self._reset_to_defaults_btn.clicked.connect
        """
        TITLE = "Reset to Defaults"

        default_values = {key: option.default
                          for key, option in
                          api.get_plugin(self.current_plugin).options.items()}

        # Check if there are any changed options
        changed_options = []
        for option_item in self.option_items:
            if option_item.val != default_values[option_item.option_name]:
                changed_options.append(option_item.option_name)

        # Prompt the user appropriately
        if len(changed_options):
            desc = "The following options will be reset to default:\n\t"
            desc += ", \n\t".join(changed_options)
            result = QMessageBox.question(self, TITLE, desc)
            if result != QMessageBox.Yes:
                # The user cancelled, so exit early.
                return

            # Change the options to default
            for option_item in self.option_items:
                option_item.set_val(default_values[option_item.option_name])

            # Change the 'enabled' to default
            self.enabled_option.set_val(True)
        else:
            desc = "There are no changes to reset"
            QMessageBox.information(
                self, TITLE, desc)

    def on_reset_overriding_streams(self):
        """
        Reset all values to default after prompting the user

        Connected to:
        - QPushButton -- Dynamic
          self._reset_overriding_btn.clicked.connect
        """
        all_stream_ids = [s.id for s in api.get_stream_configurations()]

        # Check if any streams override this
        changed_stream_ids = []
        for stream_id in all_stream_ids:
            # Check if plugin options or plugin activity is changed server-side
            opts = api.get_plugin_option_vals(
                plugin_name=self.current_plugin,
                stream_id=stream_id)
            is_active = api.is_plugin_active(
                plugin_name=self.current_plugin,
                stream_id=stream_id)

            if len(opts) or is_active is not None:
                changed_stream_ids.append(stream_id)

        TITLE = "Reset to Stream Overrides"
        if len(changed_stream_ids):
            desc = "The following streams have overrides " \
                   "that will be cleared:\n\t"

            stream_names = [s.name for s in api.get_stream_configurations()
                            if s.id in changed_stream_ids]

            desc += ", \n\t".join(stream_names)
            result = QMessageBox.question(self, TITLE, desc)
            if result != QMessageBox.Yes:
                # The user cancelled, so exit early.
                return

            # Change the options to default
            for stream_id in changed_stream_ids:
                api.set_plugin_option_vals(
                    plugin_name=self.current_plugin,
                    stream_id=stream_id,
                    option_vals={})
                api.set_plugin_active(
                    plugin_name=self.current_plugin,
                    stream_id=stream_id,
                    active=None)
        else:
            desc = "There are no streams that override the global options " \
                   "for this plugin."
            QMessageBox.information(
                self, TITLE, desc)
