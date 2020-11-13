from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget

from brainframe.client.ui.resources.ui_elements.buttons import IconButton
from brainframe.client.ui.resources.ui_elements.widgets.dialogs import \
    BrainFrameMessage


class StreamAlert(QWidget):
    def __init__(self, button_icon: QIcon, short_text: str, message_text: str,
                 *, parent: QWidget):
        super().__init__(parent=parent)

        self.button_icon = button_icon
        self.short_text = short_text
        self.message_text = message_text

        self.icon_button = self._init_icon_button()
        self.label = self._init_label()

        self._init_layout()
        self._init_style()

    def _init_icon_button(self) -> "_StreamAlertButton":
        icon_button = _StreamAlertButton(self.button_icon, self.message_text,
                                         self.short_text, parent=self)
        return icon_button

    def _init_label(self) -> QLabel:
        label = QLabel(self.short_text, parent=self)

        return label

    def _init_layout(self) -> None:
        layout = QHBoxLayout()

        layout.addWidget(self.icon_button)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setToolTip(self.message_text)


class _StreamAlertButton(IconButton):
    def __init__(self, button_icon: QIcon, message_text: str, short_text: str,
                 *, parent: QWidget):
        super().__init__(button_icon, "", parent)

        message = BrainFrameMessage.information(
            parent=self,
            title=short_text,
            message=message_text
        )

        self.clicked.connect(message.show)
