from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, \
    QTextOption
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QPushButton, \
    QVBoxLayout, QWidget

from brainframe.client.ui.resources.ui_elements.widgets.text_edit import \
    DragAndDropTextEditor


class _TextLicenseEditorUI(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.license_textbox = self._init_license_textbox()
        self.remove_license_button = self._init_remove_license_button()
        self.update_license_button = self._init_update_license_button()

        self._button_layout = self._init_button_layout()
        self._init_layout()
        self._init_style()

    def _init_license_textbox(self) -> DragAndDropTextEditor:
        license_textbox = DragAndDropTextEditor(self)
        license_textbox.placeholder_text = \
            QApplication.translate(
                "TextLicenseEditor",
                "Paste license text or drag-and-drop license file here")

        return license_textbox

    def _init_remove_license_button(self) -> QPushButton:
        button_text = self.tr("Remove License")
        remove_license_button = QPushButton(button_text, self)

        return remove_license_button

    def _init_update_license_button(self) -> QPushButton:
        button_text = QApplication.translate("TextLicenseEditor",
                                             "Update License")
        update_license_button = QPushButton(button_text, self)

        # Disabled until textbox has content
        update_license_button.setDisabled(True)

        return update_license_button

    def _init_button_layout(self) -> QHBoxLayout:
        button_layout = QHBoxLayout()

        button_layout.addWidget(self.remove_license_button)
        button_layout.addWidget(self.update_license_button)

        return button_layout

    def _init_layout(self) -> None:
        main_layout = QVBoxLayout()

        main_layout.addWidget(self.license_textbox)
        main_layout.addLayout(self._button_layout)

        # TODO: Hidden for now. May be used in future
        self.remove_license_button.hide()

        self.setLayout(main_layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.layout().setContentsMargins(0, 0, 0, 0)
        self._button_layout.setAlignment(Qt.AlignRight)

        # TODO: Verify that this works on all builds
        # https://stackoverflow.com/q/1468022/8134178
        monospace_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.license_textbox.setFont(monospace_font)

        self.license_textbox.setWordWrapMode(QTextOption.WrapAnywhere)
