from typing import Dict, Callable

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths
from .plugin_options import StreamPluginOptionsWidget, GlobalPluginOptionsWidget


class PluginConfigDialog(QDialog):

    def __init__(self, stream_id=None, parent=None):
        """

        :param stream_id: If not None, this will show options for a specific
        stream and the plugin optinos will render with the checkboxes for
        Override Global Configuration. Furthermore, when applied it will
        set the options only for the specific stream.
        :param parent:
        """
        super().__init__(parent=parent)
        loadUi(qt_ui_paths.plugin_config_dialog_ui, self)

        # Add the appropriate options widget
        if stream_id:
            options_widget = StreamPluginOptionsWidget(stream_id, parent=self)
        else:
            options_widget = GlobalPluginOptionsWidget(parent=self)
        self.plugin_options_widget = options_widget
        self.layout().addWidget(self.plugin_options_widget, 0, 1)

        # Connect signals
        self.plugin_options_widget.plugin_options_changed.connect(
            self.is_inputs_valid)

        self.stream_id = stream_id

        # self.dialog_button_box.apply.clicked.connect(self.apply)
        apply_btn = self.dialog_button_box.button(QDialogButtonBox.Apply)
        apply_func = lambda: self.plugin_options_widget.apply_changes(stream_id)
        apply_btn.clicked.connect(apply_func)

    @classmethod
    def show_dialog(cls, stream_id=None):
        dialog = cls(stream_id=stream_id)
        dialog.exec_()

    @pyqtSlot()
    def is_inputs_valid(self):
        """Sets the Apply button to Gray if the inputs are not valid or
        have not been changed.

        Connected to:
        - BasePluginOptionsWidget -- Dynamic
          [child].plugin_options_changed
        """

        is_valid = True
        if not self.plugin_options_widget.options_valid():
            is_valid = False

        buttons = QDialogButtonBox
        self.dialog_button_box.button(buttons.Ok).setEnabled(is_valid)
        self.dialog_button_box.button(buttons.Apply).setEnabled(is_valid)

    @pyqtSlot(str)
    def on_plugin_change(self, plugin_name):
        """
        :param plugin_name: The name of the plugin that has been selected
        by the plugin list.

        Connected to:
        - PluginList -- QtDesigner
          [peer].plugin_selection_changed
        """
        self.plugin_options_widget.change_plugin(plugin_name)

    def accept(self):
        """Close the window after applying the changes

        Connected to:
        - QButtonBox -- QtDesigner
          [child].accepted
        """
        self.plugin_options_widget.apply_changes()
        super().accept()
