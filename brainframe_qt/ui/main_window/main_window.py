import functools
import typing
from typing import List, Optional

import typing
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QAction, QDockWidget, QWidget

from brainframe.client.api import codecs
from brainframe.client.ui.dialogs.about_page.about_page import AboutPage
from brainframe.client.ui.dialogs.capsule_configuration.plugin_config import \
    CapsuleConfigDialog
from brainframe.client.ui.dialogs.server_configuration.server_configuration import \
    ServerConfigurationDialog
from brainframe.client.ui.dialogs.client_configuration \
    import RenderConfiguration
from brainframe.client.ui.main_window.activities import StreamConfiguration
from brainframe.client.ui.main_window.main_window_ui import MainWindowUI
from brainframe.client.ui.resources import stylesheet_watcher


class MainWindow(MainWindowUI):

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.dock_widgets: List[QDockWidget] = []
        self.activity_action_map = {
            self.toolbar.stream_activity_action: self.stream_activity,
            self.toolbar.identity_activity_action: self.identity_activity,
            self.toolbar.alert_view_activity_action: self.alert_activity
        }
        self.dialog_action_map = {
            self.toolbar.capsule_config_action: CapsuleConfigDialog,
            self.toolbar.client_config_action: RenderConfiguration,
            self.toolbar.server_config_action: ServerConfigurationDialog,
            self.toolbar.about_page_action: AboutPage
        }

        self._init_signals()

        # Explicitly make the stream activity active (helps with styling)
        # Not sure why the delay is necessary
        select_stream_activity = functools.partial(
            self.change_activity, self.toolbar.stream_activity_action)
        QTimer.singleShot(0, select_stream_activity)

    def _init_signals(self) -> None:

        self._init_activity_signals()
        self._init_dialog_signals()

        expanded_view = self.stream_activity.video_expanded_view
        expanded_view.open_stream_config_signal.connect(
            self.display_stream_configuration)
        expanded_view.stream_delete_signal.connect(
            self.close_stream_configuration)

        self.stream_activity.new_stream_button.clicked.connect(
            lambda _: self.display_stream_configuration())

    def _init_activity_signals(self) -> None:

        for action in self.activity_action_map.keys():
            action.triggered.connect(self._handle_action_click)

    def _init_dialog_signals(self) -> None:

        for action in self.dialog_action_map.keys():
            action.triggered.connect(self._handle_action_click)

    def change_activity(self, action: QAction) -> None:
        # Change action button background
        for action_ in self.toolbar.button_actions:

            button = self.toolbar.widgetForAction(action_)

            tag = "selected" if action_ is action else "deselected"
            button.setObjectName(tag)

        # Update stylesheet because we changed object names (must force reload)
        stylesheet_watcher.update_widget(self)

        # Open activity
        widget = self.activity_action_map[action]
        self.stacked_widget.setCurrentWidget(widget)

    def open_dialog(self, action) -> None:
        dialog = self.dialog_action_map[action]
        dialog.show_dialog(self)

    def display_stream_configuration(
            self, stream_conf: Optional[codecs.StreamConfiguration] = None) \
            -> None:

        for dock_widget in self.dock_widgets:
            if isinstance(dock_widget.widget(), StreamConfiguration):
                break
        else:
            dock_widget = QDockWidget(self)
            stream_configuration_widget = StreamConfiguration(self)
            dock_widget.setWidget(stream_configuration_widget)
            self.dock_widgets.append(dock_widget)

            stream_configuration_widget.stream_conf_modified.connect(
                self.stream_activity.video_thumbnail_view.add_stream_conf)
            stream_configuration_widget.stream_conf_deleted.connect(
                self.close_stream_configuration)

        self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)

        dock_widget.show()

        stream_configuration_widget = dock_widget.widget()
        stream_configuration_widget.load_from_conf(stream_conf)

    def close_stream_configuration(
            self, stream_conf: Optional[codecs.StreamConfiguration] = None) \
            -> None:

        for dock_widget in self.dock_widgets:
            stream_conf_widget = dock_widget.widget()
            if isinstance(stream_conf_widget, StreamConfiguration):
                break
            # noinspection PyUnusedLocal
            stream_conf_widget = typing.cast(StreamConfiguration,
                                             stream_conf_widget)
        else:
            # Nothing to do
            return

        # If stream_conf is passed, make sure the StreamConfiguration widget's
        # stream_conf matches
        if stream_conf is not None \
                and stream_conf_widget.stream_id != stream_conf.id:
            return

        self.dock_widgets.remove(dock_widget)
        dock_widget.close()

    def _handle_action_click(self) -> None:
        action = typing.cast(QAction, self.sender())
        if action in self.activity_action_map:
            self.change_activity(action)
        elif action in self.dialog_action_map:
            self.open_dialog(action)
