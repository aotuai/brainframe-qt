from typing import List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDockWidget, QWidget

from brainframe.client.api import codecs
from brainframe.client.ui.dialogs.about_page.about_page import AboutPage
from brainframe.client.ui.dialogs.plugin_configuration.plugin_config import \
    PluginConfigDialog
from brainframe.client.ui.dialogs.server_configuration.server_configuration import \
    ServerConfigurationDialog
from brainframe.client.ui.dialogs.video_configuration.video_configuration import \
    RenderConfiguration
from brainframe.client.ui.main_window.activities import StreamConfiguration
from brainframe.client.ui.main_window.main_window_ui import MainWindowUI


class MainWindow(MainWindowUI):

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.dock_widgets: List[QDockWidget] = []

        self._init_signals()

    def _init_signals(self):

        self._init_activity_signals()
        self._init_dialog_signals()

        thumbnail_view = self.stream_activity.video_thumbnail_view
        thumbnail_view.thumbnail_stream_clicked_signal.connect(
            self.display_stream_configuration)

        self.stream_activity.new_stream_button.clicked.connect(
            lambda _: self.display_stream_configuration())

    def _init_activity_signals(self):
        self.toolbar.stream_activity_action.triggered.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.stream_activity))
        self.toolbar.identity_activity_action.triggered.connect(
            lambda: self.stacked_widget.setCurrentWidget(
                self.identity_activity))
        self.toolbar.alert_view_activity_action.triggered.connect(
            lambda: self.stacked_widget.setCurrentWidget(
                self.alert_activity))

    def _init_dialog_signals(self):
        self.toolbar.client_config_action.triggered.connect(
            lambda: RenderConfiguration.show_dialog(self))
        self.toolbar.plugin_config_action.triggered.connect(
            lambda: PluginConfigDialog.show_dialog(self))
        self.toolbar.server_config_action.triggered.connect(
            lambda: ServerConfigurationDialog.show_dialog(self))
        self.toolbar.about_page_action.triggered.connect(
            lambda: AboutPage.show_dialog(self))

    def display_stream_configuration(
            self, stream_conf: Optional[codecs.StreamConfiguration] = None) \
            -> None:

        stream_configuration_widget = None
        for dock_widget in self.dock_widgets:
            widget = dock_widget.widget()
            if isinstance(widget, StreamConfiguration):
                stream_configuration_widget = widget

        if stream_configuration_widget is None:
            dock_widget = QDockWidget(self)
            stream_configuration_widget = StreamConfiguration(self)
            dock_widget.setWidget(stream_configuration_widget)

            self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)

            self.dock_widgets.append(dock_widget)

        stream_configuration_widget.load_from_conf(stream_conf)
