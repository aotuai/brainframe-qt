from PyQt5.QtWidgets import QLabel
from PyQt5.uic import loadUi

from brainframe_qt.ui.dialogs.capsule_configuration import capsule_utils
from brainframe_qt.ui.resources.paths import qt_ui_paths


class CapsuleListItem(QLabel):

    def __init__(self, name, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.capsule_list_item_ui, self)

        self.capsule_name = name
        self.setText(capsule_utils.pretty_snakecase(name))
