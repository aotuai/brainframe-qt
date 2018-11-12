from PyQt5.QtWidgets import QPushButton, QGridLayout

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
        options = api.get_plugin_options(self.current_plugin)
        options[0]


    def on_reset_overriding_streams(self):
        """
        Reset all values to default after prompting the user

        Connected to:
        - QPushButton -- Dynamic
          self._reset_overriding_btn.clicked.connect
        """
