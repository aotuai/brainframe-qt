from abc import abstractmethod
from typing import Generic, TypeVar

from PyQt5.QtWidgets import QWidget, QLayoutItem, QVBoxLayout

from brainframe_qt.ui.resources.mixins import BaseQMixin
from brainframe_qt.ui.resources.data_structures import SortedList

W = TypeVar("W", bound=QWidget)


# TODO: Python3.7: Inherit from Generic[W]
# TODO: This should work with all QLayouts, (as long as they define
#  insertWidget and insertItem), but I can't figure out how to
class SortedLayoutMI(BaseQMixin, QVBoxLayout):
    """Layout that keeps itself sorted by using a key function. Do NOT use
    any spacers or stretch items, or replaceWidget. They will break things"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._widgets: SortedList[W] = SortedList(key=self._sort_key,
                                                  reversed_=self._reversed())

    @abstractmethod
    def _reversed(self) -> bool:
        ...

    @abstractmethod
    def _sort_key(self, other: W) -> SortedList.Comparable:
        ...

    def addItem(self, item: QLayoutItem) -> None:
        widget: W = item.widget()
        index = self._widgets.add(widget)
        self.insertItem(index, item)

    def addWidget(self, widget: W, *args, **kwargs) -> None:
        index = self._widgets.add(widget)
        self.insertWidget(index, widget, *args, **kwargs)

    def removeItem(self, item: QLayoutItem) -> None:
        widget: W = item.widget()
        self._widgets.remove(widget)
        return super().removeItem(item)

    def removeWidget(self, widget: W) -> None:
        self._widgets.remove(widget)
        return super().removeWidget(widget)

    def takeAt(self, index: int) -> QLayoutItem:
        self._widgets.pop(index)
        return super().takeAt(index)
