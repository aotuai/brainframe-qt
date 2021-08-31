from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import QStackedWidget, QLabel, QLineEdit


class EditableLabel(QStackedWidget):
    def __init__(self, text: str, *, parent: QObject):
        super().__init__(parent=parent)

        self._label = self._init_label()
        self._line_edit = self._init_line_edit()

        self._text = ""
        self.text = text

        self._init_layout()
        self._init_style()

    def _init_label(self) -> QLabel:
        label = QLabel(parent=self)

        return label

    def _init_line_edit(self) -> QLineEdit:
        line_edit = QLineEdit(parent=self)

        return line_edit

    def _init_layout(self) -> None:
        self.addWidget(self._label)
        self.addWidget(self._line_edit)

    def _init_style(self) -> None:
        self.setAttribute(Qt.WA_StyledBackground, True)

    @property
    def text(self) -> str:
        return self._label.text()

    @text.setter
    def text(self, text: str):
        self._label.setText(text)

    def start_edit(self) -> None:
        self._line_edit.setText(self.text)
        self._line_edit.selectAll()

        self.setCurrentWidget(self._line_edit)

    def finish_edit(self) -> None:
        self.text = self._line_edit.text()

        self.setCurrentWidget(self._label)
