from enum import Enum, auto
from typing import Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QSizePolicy, QToolBar, QToolButton, \
    QWidget


class MainToolbar(QToolBar):
    class ToolbarSection(Enum):
        WINDOWED = auto()
        EXTENSION = auto()
        DIALOG = auto()
        ABOUT = auto()

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._section_termini: Dict[self.ToolbarSection, QAction] = {}

        self._init_layout()

    def _init_layout(self) -> None:

        # Create the invisible actions that we can insert other actions
        # relative to
        for toolbar_section in self.ToolbarSection:
            section_terminus = self._create_terminus_action()

            self.addAction(section_terminus)
            self._section_termini[toolbar_section] = section_terminus

        # Add spacer between extension and dialog sections
        spacer = self._create_spacer_widget()
        dialog_section_terminus \
            = self._section_termini[self.ToolbarSection.DIALOG]
        self.insertWidget(dialog_section_terminus, spacer)

        # Add separator before each section, except the first
        for toolbar_section in list(self.ToolbarSection)[1:]:
            section_terminus = self._section_termini[toolbar_section]
            self.insertSeparator(section_terminus)

    def add_action(self, icon: QIcon, text: str,
                   toolbar_section: ToolbarSection) -> QAction:
        action = QAction(icon, text, self)
        section_terminus = self._section_termini[toolbar_section]
        self.insertAction(section_terminus, action)

        button = self.widgetForAction(action)

        button.setObjectName("deselected")
        # TODO: This is supposed to make all the buttons the same width,
        #  not sure why it doesn't work. I set the button min-width to an
        #  arbitrary value in the qss instead
        button.setSizePolicy(QSizePolicy.Expanding,
                             QSizePolicy.Preferred)
        button.setCursor(Qt.PointingHandCursor)

        return action

    @property
    def button_actions(self) -> List[QAction]:
        actions = []
        for action in self.actions():
            button = self.widgetForAction(action)

            # Hidden actions are used to insert other actions. We don't care
            # about them here
            if not action.isVisible():
                continue

            if isinstance(button, QToolButton):
                actions.append(action)

        return actions

    def set_selected_action(self, action: QAction) -> None:

        for action_ in self.button_actions:
            button = self.widgetForAction(action_)

            tag = "selected" if action_ is action else "deselected"
            button.setObjectName(tag)

    def _create_terminus_action(self) -> QAction:
        """This is so that we can use QWidget.insertAction(before=...)"""
        action = QAction(self)
        action.setVisible(False)
        return action

    def _create_spacer_widget(self) -> QWidget:
        widget = QWidget(self)
        widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        return widget
