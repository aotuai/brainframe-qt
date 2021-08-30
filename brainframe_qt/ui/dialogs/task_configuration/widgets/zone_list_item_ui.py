from enum import Enum, auto

from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QLabel

from brainframe_qt.ui.resources.ui_elements.buttons import IconButton
from brainframe_qt.ui.resources.ui_elements.widgets import AspectRatioSVGWidget


class ZoneListType(Enum):
    REGION = auto()
    LINE = auto()
    ALARM = auto()
    UNKNOWN = auto()


class ZoneListItemUI(QWidget):

    _ICON_MAP = {
        ZoneListType.REGION: ":/icons/region",
        ZoneListType.LINE: ":/icons/line",
        ZoneListType.ALARM: ":/icons/alarm",
        ZoneListType.UNKNOWN: ":/icons/question_mark",
    }

    _UNKNOWN_NAME_STR = "[ZoneListItem]"

    def __init__(self, *, parent: QObject):
        super().__init__(parent=parent)

        self._entry_name = self._UNKNOWN_NAME_STR
        self._entry_type = ZoneListType.UNKNOWN

        self.entry_icon = self._init_entry_icon()
        self.name_label = self._init_name_label()
        self.edit_button = self._init_edit_button()
        self.trash_button = self._init_trash_button()

        self._init_layout()
        self._init_style()

    def _init_entry_icon(self) -> AspectRatioSVGWidget:
        icon_path = self._ICON_MAP[self._entry_type]
        icon = AspectRatioSVGWidget(icon_path, self)

        icon.setObjectName("entry_icon")

        return icon

    def _init_name_label(self) -> QLabel:
        label = QLabel(self._entry_name, parent=self)

        return label

    def _init_edit_button(self) -> IconButton:
        edit_button = IconButton(self.parent())

        edit_button.setIcon(QIcon(":/icons/edit"))
        edit_button.setToolTip("Edit")

        edit_button.setFlat(True)

        return edit_button

    def _init_trash_button(self) -> IconButton:
        trash_button = IconButton(self.parent())

        trash_button.setIcon(QIcon(":/icons/trash"))
        trash_button.setToolTip("Delete")

        trash_button.setFlat(True)

        return trash_button

    def _init_layout(self) -> None:
        layout = QHBoxLayout()

        layout.addWidget(self.entry_icon)
        layout.addWidget(self.name_label)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.trash_button)

        self.setLayout(layout)

    def _init_style(self) -> None:
        self.setAttribute(Qt.WA_StyledBackground, True)

    @property
    def entry_name(self) -> str:
        return self._entry_name

    @entry_name.setter
    def entry_name(self, entry_name: str) -> None:
        self._entry_name = entry_name
        self.name_label.setText(entry_name)

    @property
    def entry_type(self) -> ZoneListType:
        return self._entry_type

    @entry_type.setter
    def entry_type(self, entry_type: ZoneListType) -> None:
        self._entry_type = entry_type

        icon_path = self._ICON_MAP[entry_type]
        self.entry_icon.load(icon_path)
