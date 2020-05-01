from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QLabel, QSizePolicy, QToolBar, \
    QToolButton, \
    QWidget


class MainToolbar(QToolBar):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        stream_text = self.tr("Streams")
        identity_text = self.tr("Identities")
        alert_text = self.tr("Alerts")
        task_config_text = self.tr("Tasks")
        plugin_config_text = self.tr("Plugins")
        client_config_text = self.tr("Client")
        server_config_text = self.tr("Server")
        about_page_text = self.tr("About")

        self.stream_activity_action \
            = self._init_action(":/icons/new_stream", stream_text)
        self.identity_activity_action \
            = self._init_action(":/icons/person", identity_text)
        self.alert_view_activity_action \
            = self._init_action(":/icons/alert_view", alert_text)
        self.task_config_action \
            = self._init_action(":/icons/settings_gear", task_config_text)
        self.plugin_config_action \
            = self._init_action(":/icons/global_plugin_config",
                                plugin_config_text)
        self.client_config_action \
            = self._init_action(":/icons/client_config", client_config_text)
        self.server_config_action \
            = self._init_action(":/icons/server_config", server_config_text)
        self.about_page_action \
            = self._init_action(":/icons/info", about_page_text)

        self._init_layout()
        self._init_style()

    def _init_action(self, icon_path: str, text: str):
        icon = QIcon(icon_path)
        return QAction(icon, text, self)

    def _init_layout(self):
        self.addAction(self.stream_activity_action)
        self.addAction(self.identity_activity_action)
        self.addAction(self.alert_view_activity_action)

        self.addWidget(self._create_spacer_widget())

        self.addSeparator()

        # self.addAction(self.task_config_action)
        self.addAction(self.plugin_config_action)
        self.addAction(self.client_config_action)
        self.addAction(self.server_config_action)

        self.addSeparator()

        self.addAction(self.about_page_action)

    def _init_style(self):
        for action in self.actions():
            widget = self.widgetForAction(action)
            if not isinstance(widget, QToolButton):
                continue

            # TODO: This is supposed to make all the buttons the same width,
            #  not sure why it doesn't work
            widget.setSizePolicy(QSizePolicy.Expanding,
                                 QSizePolicy.Preferred)

            widget.setCursor(Qt.PointingHandCursor)

    def _create_spacer_widget(self) -> QWidget:
        widget = QWidget(self)
        widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        return widget
