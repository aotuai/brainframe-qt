import collections
import typing
from pathlib import Path
from typing import DefaultDict, Set

from PyQt5.QtCore import QFileSystemWatcher
from PyQt5.QtWidgets import QWidget


class _StylesheetWatcher:
    """Live-reloading of stylesheets when the underlying file is changed, or
    when .update() is called manually for a stylesheet
    """

    _singleton = typing.cast("StylesheetWatcher", None)

    # def __new__(cls, *args, **kwargs):
    #     if not cls._singleton:
    #         cls._singleton = super().__new__(cls, *args, **kwargs)
    #     return cls._singleton

    def __init__(self):

        # Map of the stylesheets to the widgets they're applied to
        self._widget_sheet_map: DefaultDict[Path, Set[QWidget]] \
            = collections.defaultdict(set)
        self._watcher = typing.cast(QFileSystemWatcher, None)

    def watch(self, widget, stylesheet_path) -> None:
        """Create link between widget and stylesheet and set up a file watcher
        """

        # Defer initializing the watcher until the event loop has started
        if self._watcher is None:
            self._watcher = QFileSystemWatcher()

        self._widget_sheet_map[stylesheet_path].add(widget)
        self._watcher.addPath(str(stylesheet_path))

        # noinspection PyUnresolvedReferences
        self._watcher.fileChanged.connect(self.update)

        self.update()

    def unwatch(self, widget, stylesheet_path) -> None:

        watched_widgets = self._widget_sheet_map[stylesheet_path]
        watched_widgets.remove(widget)

        # Stop watching the path if we no longer have subscribed widgets
        if not watched_widgets:
            self._watcher.removePath(str(stylesheet_path))
            self._widget_sheet_map.pop(stylesheet_path)

    def update(self) -> None:
        """Force reload the stylesheet when the underlying file has changed"""
        for stylesheet_path, widgets in self._widget_sheet_map.items():

            # Stylesheet as text
            raw_stylesheet = stylesheet_path.read_text()

            for widget in widgets:
                widget.setStyleSheet(raw_stylesheet)


stylesheet_watcher = _StylesheetWatcher()
