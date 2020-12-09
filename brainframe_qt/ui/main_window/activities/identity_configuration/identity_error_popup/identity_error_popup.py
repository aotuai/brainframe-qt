from typing import Set

from PyQt5.QtWidgets import QDialog, QHeaderView, QTreeWidgetItem
from PyQt5.uic import loadUi

from brainframe_qt.ui.resources.paths import qt_ui_paths


# TODO: Use Python3.7 @dataclass attribute
class IdentityError:

    def __init__(self, value, error=""):
        self.value: str = value
        self.error: str = error
        self.children: Set["IdentityError"] = set()


class IdentityErrorPopup(QDialog):

    def __init__(self, errors: Set[IdentityError], parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.identity_error_popup_ui, self)

        for identity_error in errors:

            identity_tree_item = QTreeWidgetItem(
                self.error_tree,
                [identity_error.value, identity_error.error])

            for encoding_error in identity_error.children:

                encoding_tree_item = QTreeWidgetItem(
                    identity_tree_item,
                    [encoding_error.value, encoding_error.error])

                for image_error in encoding_error.children:
                    QTreeWidgetItem(
                        encoding_tree_item,
                        [image_error.value, image_error.error])

        self.error_tree.expandAll()
        self.error_tree.header().setSectionResizeMode(
            QHeaderView.ResizeToContents)

    @classmethod
    def show_errors(cls, errors: Set[IdentityError], parent):
        error_widget = cls(errors, parent)
        error_widget.exec_()
