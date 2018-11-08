from typing import Dict, Callable

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.ui.resources.paths import qt_ui_paths


class PluginConfigDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        loadUi(qt_ui_paths.plugin_config_dialog_ui, self)
        self.plugin_options_widget.plugin_options_changed.connect(
            self.is_inputs_valid)

        # self.dialog_button_box.apply.clicked.connect(self.apply)
        apply_btn = self.dialog_button_box.button(QDialogButtonBox.Apply)
        apply_btn.clicked.connect(self.plugin_options_widget.apply_changes)

    @classmethod
    def show_dialog(cls):
        dialog = cls()
        dialog.exec_()

    @pyqtSlot()
    def is_inputs_valid(self):
        """Sets the Apply button to Gray if the inputs are not valid or
        have not been changed.

        Connected to:
        - PluginOptionsWidget -- Dynamic
          [child].plugin_options_changed
        """

        is_valid = True
        if not self.plugin_options_widget.options_valid():
            is_valid = False

        buttons = QDialogButtonBox
        self.dialog_button_box.button(buttons.Ok).setEnabled(is_valid)
        self.dialog_button_box.button(buttons.Apply).setEnabled(is_valid)

    def accept(self):
        """Close the window after applying the changes

        Connected to:
        - QButtonBox -- QtDesigner
          [child].accepted
        """
        self.plugin_options_widget.apply_changes()
        super().accept()

