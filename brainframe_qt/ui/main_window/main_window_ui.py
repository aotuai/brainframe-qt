from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QStackedWidget, \
    QToolBar, QWidget

from brainframe.client.ui.main_window.activities.identity_configuration \
    import IdentityConfiguration
from brainframe.client.ui.main_window.activities.stream_activity import \
    StreamActivity
from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.paths import qt_qss_paths


class MainWindowUI(QMainWindow):

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.stacked_widget = self._init_tab_widget()
        self.toolbar = self._init_toolbar()

        self.stream_activity = self._init_stream_activity()
        self.identity_activity = self._init_identity_activity()

        self._init_layout()
        self._init_style()

    def _init_tab_widget(self) -> QStackedWidget:
        tab_widget = QStackedWidget(self)
        return tab_widget

    def _init_stream_activity(self) -> StreamActivity:
        stream_activity = StreamActivity(self)
        return stream_activity

    def _init_identity_activity(self) -> IdentityConfiguration:
        identity_activity = IdentityConfiguration(self)
        return identity_activity

    def _init_toolbar(self) -> QToolBar:
        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        return toolbar

    def _init_layout(self):
        self.setCentralWidget(self.stacked_widget)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

        stream_activity_icon = QIcon(":/icons/new_stream")
        identity_activity_icon = QIcon(":/icons/person")
        alert_view_activity_icon = QIcon(":/icons/alert_view")
        about_page_icon = QIcon(":/icons/info")
        task_config_icon = QIcon(":/icons/settings_gear")
        plugin_config_icon = QIcon(":/icons/global_plugin_config")
        video_config_icon = QIcon(":/icons/video_settings")
        server_config_icon = QIcon(":/icons/server_config")

        def spacer_widget():
            widget = QWidget(self.toolbar)
            widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            return widget

        # TODO: Switch to QActions?
        self.toolbar.addAction(stream_activity_icon, "Streams")
        self.toolbar.addAction(identity_activity_icon, "Identities")
        self.toolbar.addAction(alert_view_activity_icon, "Alerts")

        self.toolbar.addWidget(spacer_widget())

        self.toolbar.addAction(task_config_icon, "Tasks")
        self.toolbar.addAction(plugin_config_icon, "Plugins")
        self.toolbar.addAction(video_config_icon, "Render")
        self.toolbar.addAction(server_config_icon, "Server")

        self.toolbar.addSeparator()

        self.toolbar.addAction(about_page_icon, "About")

        self.stacked_widget.addWidget(self.stream_activity)
        self.stacked_widget.addWidget(self.identity_activity)

    def _init_style(self):
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.resize(1400, 900)

        stylesheet_watcher.watch(self, qt_qss_paths.main_window_qss)
