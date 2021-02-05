from PyQt5.QtWidgets import QWidget, QLineEdit, QFormLayout, QVBoxLayout, \
    QPushButton, QSizePolicy


class AotuLoginFormUI(QWidget):
    def __init__(self, *, parent: QWidget):
        super().__init__(parent=parent)

        self.email_field = self._init_email_field()
        self.password_field = self._init_password_field()

        self.log_in_button = self._init_log_in_button()

        self.form_layout = self._init_form_layout()

        self._init_layout()

    def _init_email_field(self) -> QLineEdit:
        email_field = QLineEdit(self)

        email_field.setPlaceholderText(self.tr("Email"))

        return email_field

    def _init_password_field(self) -> QLineEdit:
        password_field = QLineEdit(self)

        password_field.setPlaceholderText(self.tr("Password"))
        password_field.setEchoMode(QLineEdit.Password)

        return password_field

    def _init_log_in_button(self) -> QPushButton:
        login_button = QPushButton(parent=self)

        login_button.setText(self.tr("Log in"))
        login_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        return login_button

    def _init_form_layout(self) -> QFormLayout:
        form_layout = QFormLayout()

        form_layout.addRow(self.tr("Email"), self.email_field)
        form_layout.addRow(self.tr("Password"), self.password_field)

        return form_layout

    def _init_layout(self):
        layout = QVBoxLayout()

        layout.addLayout(self.form_layout)
        layout.addWidget(self.log_in_button)

        self.setLayout(layout)
