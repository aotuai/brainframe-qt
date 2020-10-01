from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QDialogButtonBox, \
    QPushButton, QWidget
from PyQt5.uic import loadUi

from brainframe.client.extensions import DialogActivity
from brainframe.client.ui.resources.paths import qt_ui_paths
from .capsule_options import GlobalCapsuleOptionsWidget, \
    StreamCapsuleOptionsWidget


class CapsuleConfigActivity(DialogActivity):
    _built_in = True

    def open(self, *, parent: QWidget):
        CapsuleConfigDialog.show_dialog(parent=parent)

    def window_title(self) -> str:
        return QApplication.translate("CapsuleConfigActivity",
                                      "Capsule Configuration")

    @staticmethod
    def icon() -> QIcon:
        return QIcon(":/icons/capsule_toolbar")

    @staticmethod
    def short_name() -> str:
        return QApplication.translate("CapsuleConfigActivity", "Capsules")


class CapsuleConfigDialog(QDialog):

    def __init__(self, stream_id=None, parent=None):
        """

        :param stream_id: If not None, this will show options for a specific
        stream and the capsule options will render with the checkboxes for
        Override Global Configuration. Furthermore, when applied it will
        set the options only for the specific stream.
        :param parent:
        """
        super().__init__(parent=parent)
        loadUi(qt_ui_paths.capsule_config_dialog_ui, self)

        # Add the appropriate options widget
        if stream_id:
            options_widget = StreamCapsuleOptionsWidget(stream_id, parent=self)
        else:
            options_widget = GlobalCapsuleOptionsWidget(parent=self)
        self.capsule_options_widget = options_widget
        self.layout().addWidget(self.capsule_options_widget, 1, 1)

        # Connect signals
        self.capsule_options_widget.capsule_options_changed.connect(
            self.is_inputs_valid)

        self.stream_id = stream_id

        # self.dialog_button_box.apply.clicked.connect(self.apply)
        apply_btn: QPushButton = self.dialog_button_box.button(
            QDialogButtonBox.Apply)
        apply_btn.clicked.connect(
            lambda: self.capsule_options_widget.apply_changes(stream_id))

        # Set all buttons that require a capsule to be loaded to disabled,
        # until a capsule is 'set' they shouldn't be usable.
        self.set_buttons_disabled(True)

    def set_buttons_disabled(self, val: bool):
        self.dialog_button_box.button(QDialogButtonBox.Apply).setDisabled(val)
        self.dialog_button_box.button(QDialogButtonBox.Ok).setDisabled(val)
        self.capsule_options_widget.setDisabled(val)

    @classmethod
    def show_dialog(cls, parent, stream_id=None):
        dialog = cls(stream_id=stream_id, parent=parent)
        dialog.exec_()

    @pyqtSlot()
    def is_inputs_valid(self):
        """Sets the Apply button to Gray if the inputs are not valid or
        have not been changed.

        Connected to:
        - BaseCapsuleOptionsWidget -- Dynamic
          [child].capsule_options_changed
        """

        is_valid = True
        if not self.capsule_options_widget.options_valid():
            is_valid = False

        buttons = QDialogButtonBox
        self.dialog_button_box.button(buttons.Ok).setEnabled(is_valid)
        self.dialog_button_box.button(buttons.Apply).setEnabled(is_valid)

    @pyqtSlot(str)
    def on_capsule_change(self, capsule_name):
        """
        :param capsule_name: The name of the capsule that has been selected
        by the capsule list.

        Connected to:
        - CapsuleList -- QtDesigner
          [peer].capsule_selection_changed
        """
        self.capsule_options_widget.change_capsule(capsule_name)

        # Now that a capsule is loaded, allow the user to interact with buttons
        self.set_buttons_disabled(False)

    def accept(self):
        """Close the window after applying the changes

        Connected to:
        - QButtonBox -- QtDesigner
          [child].accepted
        """
        self.capsule_options_widget.apply_changes()
        super().accept()
