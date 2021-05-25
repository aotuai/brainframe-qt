from PyQt5.QtWidgets import QWidget, QFormLayout, QVBoxLayout, QPushButton


class AotuLoginFormUI(QWidget):
    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)

        self.oauth_button = self._init_oauth_button()

        self.form_layout = self._init_form_layout()

        self._init_layout()

    def _init_oauth_button(self) -> QPushButton:
        oauth_button = QPushButton(self)
        oauth_button.setText(self.tr("Sign in using OAuth"))

        return oauth_button

    def _init_form_layout(self) -> QFormLayout:
        form_layout = QFormLayout()

        form_layout.addRow(self.oauth_button)

        return form_layout

    def _init_layout(self):
        layout = QVBoxLayout()

        layout.addLayout(self.form_layout)

        self.setLayout(layout)
