from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QWidget

from brainframe.client.ui.dialogs.alarm_view.alarm_view import AlarmView
from brainframe.client.ui.main_window.activities.identity_configuration \
    import IdentityConfiguration
from brainframe.client.ui.main_window.activities.stream_activity import \
    StreamActivity
from brainframe.client.ui.main_window.toolbar import MainToolbar
from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.paths import qt_qss_paths


class MainWindowUI(QMainWindow):

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.stacked_widget = self._init_tab_widget()
        self.toolbar = self._init_toolbar()

        self.stream_activity = self._init_stream_activity()
        self.identity_activity = self._init_identity_activity()
        self.alert_activity = self._init_alert_activity()

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

    def _init_alert_activity(self) -> AlarmView:
        alert_activity = AlarmView(self)

        return alert_activity

    def _init_toolbar(self) -> MainToolbar:
        toolbar = MainToolbar(self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        return toolbar

    def _init_layout(self) -> None:
        self.setCentralWidget(self.stacked_widget)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

        self.stacked_widget.addWidget(self.stream_activity)
        self.stacked_widget.addWidget(self.identity_activity)
        self.stacked_widget.addWidget(self.alert_activity)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.resize(1400, 900)

        stylesheet_watcher.watch(self, qt_qss_paths.main_window_qss)
