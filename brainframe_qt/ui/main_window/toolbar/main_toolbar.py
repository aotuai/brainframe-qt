from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QToolBar, QSizePolicy, QToolButton, \
    QWidget


class MainToolbar(QToolBar):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        stream_text = self.tr("Streams")
        identity_text = self.tr("Identities")
        alert_text = self.tr("Alerts")
        task_config_text = self.tr("Tasks")
        capsule_config_text = self.tr("Capsules")
        client_config_text = self.tr("Client")
        server_config_text = self.tr("Server")
        about_page_text = self.tr("About")

        self.stream_activity_action \
            = self._init_action(":/icons/stream_toolbar", stream_text)
        self.identity_activity_action \
            = self._init_action(":/icons/identity_toolbar", identity_text)
        self.alert_view_activity_action \
            = self._init_action(":/icons/alert_view", alert_text)
        self.task_config_action \
            = self._init_action(":/icons/settings_gear", task_config_text)
        self.capsule_config_action \
            = self._init_action(":/icons/capsule_toolbar",
                                capsule_config_text)
        self.client_config_action \
            = self._init_action(":/icons/client_config", client_config_text)
        self.server_config_action \
            = self._init_action(":/icons/server_config", server_config_text)
        self.about_page_action \
            = self._init_action(":/icons/info", about_page_text)

        self._init_layout()
        self._init_style()

    def _init_action(self, icon_path: str, text: str) -> QAction:
        icon = QIcon(icon_path)
        return QAction(icon, text, self)

    def _init_layout(self) -> None:
        self.addAction(self.stream_activity_action)
        self.addAction(self.identity_activity_action)
        self.addAction(self.alert_view_activity_action)

        self.addWidget(self._create_spacer_widget())

        self.addSeparator()

        # self.addAction(self.task_config_action)
        self.addAction(self.capsule_config_action)
        self.addAction(self.client_config_action)
        self.addAction(self.server_config_action)

        self.addSeparator()

        self.addAction(self.about_page_action)

    def _init_style(self) -> None:
        for action in self.button_actions:
            button = self.widgetForAction(action)

            button.setObjectName("unselected")

            # TODO: This is supposed to make all the buttons the same width,
            #  not sure why it doesn't work. I set the button min-width to an
            #  arbitrary value in the qss instead
            button.setSizePolicy(QSizePolicy.Expanding,
                                 QSizePolicy.Preferred)

            button.setCursor(Qt.PointingHandCursor)

    @property
    def button_actions(self) -> List[QAction]:
        actions = []
        for action in self.actions():
            button = self.widgetForAction(action)
            if isinstance(button, QToolButton):
                actions.append(action)

        return actions

    def _create_spacer_widget(self) -> QWidget:
        widget = QWidget(self)
        widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        return widget
