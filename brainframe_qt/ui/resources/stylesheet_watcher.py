import collections
import typing
from pathlib import Path
from typing import DefaultDict, Dict, Set

from PyQt5.QtCore import QFileSystemWatcher
from PyQt5.QtWidgets import QWidget


class _StylesheetWatcher:
    """Live-reloading of stylesheets when the underlying file is changed, or
    when .update() is called manually for a stylesheet
    """

    def __init__(self):

        # Map of the stylesheets to the widgets they're applied to
        self._widget_sheet_map: Dict[QWidget, Path] = {}
        self._sheet_widget_map: DefaultDict[Path, Set[QWidget]] \
            = collections.defaultdict(set)

        # Defer initializing the watcher until .watch() is first called
        self._watcher = typing.cast(QFileSystemWatcher, None)

    def watch(self, widget: QWidget, stylesheet_path: Path) -> None:
        """Create link between widget and stylesheet and set up a file watcher
        """

        self._sheet_widget_map[stylesheet_path].add(widget)
        self._widget_sheet_map[widget] = stylesheet_path

        # Defer initializing the watcher until the event loop has started
        if self._watcher is None:
            self._watcher = QFileSystemWatcher()
        self._watcher.addPath(str(stylesheet_path))
        # noinspection PyUnresolvedReferences
        self._watcher.fileChanged.connect(lambda: self.update_widget(widget))

        self.update_widget(widget)

    def unwatch_widget(self, widget) -> None:
        """Stop watching the stylesheet for the widget"""

        stylesheet_path = self._widget_sheet_map.pop(widget)
        watched_widgets = self._sheet_widget_map[stylesheet_path]
        watched_widgets.remove(widget)

        # Stop watching the path if we no longer have subscribed widgets
        if not watched_widgets:
            self._watcher.removePath(str(stylesheet_path))
            self._sheet_widget_map.pop(stylesheet_path)

    @staticmethod
    def _update(widget: QWidget, raw_stylesheet: str):
        widget.setStyleSheet(raw_stylesheet)

    def update_stylesheet(self, stylesheet_path: Path):
        """Force reload the stylesheet when the underlying file has changed"""

        for widget in self._sheet_widget_map[stylesheet_path]:
            self.update_widget(widget)

    def update_widget(self, widget: QWidget) -> None:
        """Force reload the stylesheet of the specified widget"""

        stylesheet_path = self._widget_sheet_map[widget]
        raw_stylesheet = stylesheet_path.read_text()
        self._update(widget, raw_stylesheet)


stylesheet_watcher = _StylesheetWatcher()
