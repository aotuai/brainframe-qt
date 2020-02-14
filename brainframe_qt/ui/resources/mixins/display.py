from abc import abstractmethod

from PyQt5.QtCore import pyqtProperty
from PyQt5.QtWidgets import QWidget

from brainframe.client.ui.resources.mixins import BaseMixin


class ExpandableMI(BaseMixin):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._expanded = True

    @pyqtProperty(bool)
    def expanded(self) -> bool:
        return self._expanded

    @expanded.setter
    def expanded(self, expanded: bool) -> None:
        self._expanded = expanded
        self.expansion_changed()

    def toggle_expansion(self):
        # noinspection PyPropertyAccess
        self.expanded = not self.expanded

    @abstractmethod
    def expansion_changed(self):
        ...
