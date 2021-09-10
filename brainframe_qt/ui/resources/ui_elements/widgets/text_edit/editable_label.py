from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QKeyEvent, QValidator
from PyQt5.QtWidgets import QStackedWidget, QLabel, QLineEdit


class EditableLabel(QStackedWidget):
    text_changed = pyqtSignal(str)

    def __init__(self, label: QLabel, line_edit: QLineEdit, *, parent: QObject):
        super().__init__(parent=parent)

        self._label = label
        self._line_edit = line_edit

        self.editable = True
        """If this is False, editing text is disabled"""
        self._editing = False

        self._init_layout()
        self._init_style()

        self._init_signals()

    def _init_layout(self) -> None:
        self.addWidget(self._label)
        self.addWidget(self._line_edit)

    def _init_style(self) -> None:
        self.setAttribute(Qt.WA_StyledBackground, True)

    def _init_signals(self) -> None:
        self._line_edit.editingFinished.connect(self.finish_edit)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if self._editing and event.key() == Qt.Key_Escape:
            self.cancel_edit()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if not self.editable:
            return

        if not self._editing:
            self.start_edit()

    @property
    def text(self) -> str:
        return self._label.text()

    @text.setter
    def text(self, text: str) -> None:
        self._label.setText(text)

    @property
    def validator(self) -> QValidator:
        return self._line_edit.validator()

    @validator.setter
    def validator(self, validator: QValidator) -> None:
        self._line_edit.setValidator(validator)

    def cancel_edit(self) -> None:
        if not self._editing:
            return

        # Block signals to prevent out-focus event from self._line_edit triggering
        # self.finish_edit
        self._line_edit.blockSignals(True)
        self.setCurrentWidget(self._label)
        self._line_edit.blockSignals(False)

        self._editing = False

    def finish_edit(self) -> None:
        if not self.editable:
            self.cancel_edit()
            return

        if not self._editing:
            return

        self.text = self._line_edit.text()

        self.setCurrentWidget(self._label)

        self._editing = False

        self.text_changed.emit(self.text)

    def start_edit(self) -> None:
        if not self.editable or self._editing:
            return

        self._line_edit.setText(self.text)

        self._line_edit.selectAll()
        self._line_edit.setFocus()

        self.setCurrentWidget(self._line_edit)

        self._editing = True