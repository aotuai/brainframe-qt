from typing import Dict, Optional

import typing
from PyQt5.QtWidgets import QAction, QWidget
from brainframe.api import bf_codecs

from brainframe_qt.extensions import AboutActivity, ClientActivity, \
    ClientExtension, DialogActivity, WindowedActivity
from brainframe_qt.ui.dialogs import AboutPageActivity, AlertActivity, \
    CapsuleConfigActivity, ClientConfigActivity, ServerConfigActivity
from brainframe_qt.ui.main_window.activities import IdentityActivity, \
    StreamActivity, StreamConfiguration
from brainframe_qt.ui.main_window.main_window_ui import MainWindowUI
from brainframe_qt.ui.main_window.toolbar import MainToolbar
from brainframe_qt.ui.main_window.video_thumbnail_view import \
    VideoThumbnailView
from brainframe_qt.ui.resources import stylesheet_watcher


class MainWindow(MainWindowUI):

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._action_activity_map: Dict[QAction, ClientActivity] = {}
        self._activity_widget_map: Dict[WindowedActivity, QWidget] = {}

        # TODO: This is so we can manually connect signals between the
        #       StreamConfiguration sidebar and the StreamView widget. It would
        #       be nice to have a first-class way of interacting with the
        #       sidebar
        self._stream_activity = typing.cast(StreamActivity, None)

        self._init_builtin_activities()
        self._init_extension_activities()

        self._init_signals()

    def _init_signals(self) -> None:
        self._init_sidebar_signals()

    def _init_builtin_activities(self):

        self._stream_activity = StreamActivity()

        for activity in (
                self._stream_activity,
                IdentityActivity(),
                AlertActivity(),
                AboutPageActivity(),
                CapsuleConfigActivity(),
                ClientConfigActivity(),
                ServerConfigActivity()
        ):
            self._init_activity(activity)

    def _init_extension_activities(self):

        for extension in ClientExtension.__subclasses__():
            for activity_cls in extension.activities():
                activity = activity_cls()
                self._init_activity(activity)

    def _init_activity(self, activity: ClientActivity):

        toolbar_section = self._get_toolbar_section_for_activity(activity)

        action = self.toolbar.add_action(
            icon=activity.icon(),
            text=activity.short_name(),
            toolbar_section=toolbar_section)

        self._action_activity_map[action] = activity

        if isinstance(activity, WindowedActivity):
            widget = activity.main_widget(parent=self)

            self.stacked_widget.addWidget(widget)
            self._activity_widget_map[activity] = widget

            action.triggered.connect(lambda: self.change_activity(activity))
        elif isinstance(activity, DialogActivity):
            action.triggered.connect(lambda: activity.open(parent=self))

        self.toolbar.set_selected_action(self._current_action)

    def change_activity(self, activity: WindowedActivity):

        prev_activity: WindowedActivity = self._current_activity
        # TODO: Call this
        # prev_activity.on_hide()

        action = self._action_for_activity(activity)
        self.toolbar.set_selected_action(action)

        # Update stylesheet because we changed object names (must force reload)
        stylesheet_watcher.update_widget(self)

        widget = self._activity_widget_map[activity]
        self.stacked_widget.setCurrentWidget(widget)

        # TODO:
        # activity.on_show()

    def _init_sidebar_signals(self) -> None:

        def display_stream_configuration(
                stream_conf: Optional[bf_codecs.StreamConfiguration]):

            stream_configuration = StreamConfiguration(self)
            stream_configuration.load_from_conf(stream_conf)
            self.show_sidebar_widget(stream_configuration)

        def toggle_stream_configuration(
                stream_conf: Optional[bf_codecs.StreamConfiguration]):
            """Toggle the stream configuration if the passed stream_conf is
            the same as the displayed one"""
            sidebar_widget = self.sidebar_dock_widget.widget()
            if isinstance(sidebar_widget, StreamConfiguration) \
                    and sidebar_widget.isVisible() \
                    and sidebar_widget.stream_id == stream_conf.id:
                close_stream_configuration()
            else:
                display_stream_configuration(stream_conf)

        def close_stream_configuration():
            sidebar_widget = self.sidebar_dock_widget.widget()
            if isinstance(sidebar_widget, StreamConfiguration):
                self.close_sidebar_widget()

        def change_stream_configuration(
                stream_conf: bf_codecs.StreamConfiguration
        ) -> None:
            sidebar_widget = self.sidebar_dock_widget.widget()
            if not isinstance(sidebar_widget, StreamConfiguration):
                return

            sidebar_widget.load_from_conf(stream_conf)

        stream_view = self._activity_widget_map[self._stream_activity]
        thumbnail_view: VideoThumbnailView = stream_view.video_thumbnail_view
        thumbnail_view.stream_clicked.connect(change_stream_configuration)

        expanded_view = stream_view.video_expanded_view
        expanded_view.toggle_stream_config_signal.connect(
            toggle_stream_configuration)
        expanded_view.stream_delete_signal.connect(
            close_stream_configuration)

        # TODO: ...
        stream_view.new_stream_button.clicked.connect(
            lambda: display_stream_configuration(None))

    def close_sidebar_widget(self):
        # TODO: What happens to previous widget
        self.sidebar_dock_widget.setWidget(None)
        self.sidebar_dock_widget.hide()

    def show_sidebar_widget(self, widget: QWidget):
        if widget is self.sidebar_dock_widget.widget():
            # Nothing to do
            return

        # Clear the current widget
        if self.sidebar_dock_widget.widget() is not None:
            self.close_sidebar_widget()

        self.sidebar_dock_widget.setWidget(widget)

        self._connect_sidebar_widget_signals()

        self.sidebar_dock_widget.show()

    def _action_for_activity(self, activity: ClientActivity) -> QAction:

        for action, activity_ in self._action_activity_map.items():
            if activity_ is activity:
                return action

        raise RuntimeError(f"Unknown activity {activity}")

    def _connect_sidebar_widget_signals(self) -> None:

        sidebar_widget = self.sidebar_dock_widget.widget()

        if isinstance(sidebar_widget, StreamConfiguration):
            stream_view = self._activity_widget_map[self._stream_activity]
            sidebar_widget.stream_conf_modified.connect(
                stream_view.video_thumbnail_view.add_stream)
            sidebar_widget.stream_conf_modified.connect(
                self._handle_stream_config_modification)

            sidebar_widget.stream_conf_deleted.connect(
                self.close_sidebar_widget)

    @property
    def _current_activity(self) -> WindowedActivity:
        current_widget = self.stacked_widget.currentWidget()

        for activity, widget in self._activity_widget_map.items():
            if widget is current_widget:
                return activity

        raise RuntimeError("Unknown current widget state")

    @property
    def _current_action(self) -> QAction:
        return self._action_for_activity(self._current_activity)

    @staticmethod
    def _get_toolbar_section_for_activity(activity: ClientActivity) \
            -> MainToolbar.ToolbarSection:
        # noinspection PyProtectedMember
        if not activity._built_in:
            return MainToolbar.ToolbarSection.EXTENSION

        if isinstance(activity, WindowedActivity):
            return MainToolbar.ToolbarSection.WINDOWED
        elif isinstance(activity, AboutActivity):
            return MainToolbar.ToolbarSection.ABOUT
        elif isinstance(activity, DialogActivity):
            return MainToolbar.ToolbarSection.DIALOG
        else:
            raise ValueError

    def _handle_stream_config_modification(
            self, stream_conf: bf_codecs.StreamConfiguration) \
            -> None:

        sidebar_widget = self.sidebar_dock_widget.widget()

        # Failsafe
        if not isinstance(sidebar_widget, StreamConfiguration):
            return

        stream_view = self._activity_widget_map[self._stream_activity]
        stream_view.open_expanded_view(stream_conf)
