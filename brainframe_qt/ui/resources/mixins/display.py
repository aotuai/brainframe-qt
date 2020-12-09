from abc import abstractmethod

from PyQt5.QtCore import pyqtProperty, pyqtSignal
from PyQt5.QtWidgets import QWidget

from brainframe_qt.ui.resources.mixins import BaseWidgetMixin


class ExpandableMI(BaseWidgetMixin):

    def __init_subclass__(cls, **kwargs):
        # This hack is required because of the magic PyQt does to properties.
        # A pyqtProperty is bound to the class that they are first created on.
        # This creates a new property that is attached to the child class.
        cls.expanded = pyqtProperty(bool, cls.expanded.fget, cls.expanded.fset)

        # This is required here because of the magic PyQt does to signals.
        # If expanded is simply declared as an attribute of the base mixin
        # class, PyQt will be unable to connect the signal from a subclass.
        # Not really sure why, but this works.
        cls.expansion_changed = pyqtSignal(bool)
        super().__init_subclass__()

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._expanded = True

    @pyqtProperty(bool)
    def expanded(self) -> bool:
        return self._expanded

    @expanded.setter
    def expanded(self, expanded: bool) -> None:
        self._expanded = expanded
        self.expand(expanded)
        self.expansion_changed.emit(expanded)

    def set_expanded(self, expanded: bool) -> None:
        """Equivalent to @expanded.setter, but as a convenience method for
        lambdas"""
        self.expanded = expanded

    def toggle_expansion(self):
        # noinspection PyPropertyAccess
        self.expanded = not self.expanded

    @abstractmethod
    def expand(self, expanding: bool):
        ...
