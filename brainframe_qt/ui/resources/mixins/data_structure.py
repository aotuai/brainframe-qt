from abc import abstractmethod

from PyQt5.QtWidgets import QLayout

from brainframe_qt.ui.resources.mixins import BaseWidgetMixin


class IterableMI(BaseWidgetMixin):

    def __iter__(self):
        layout = self.iterable_layout()
        return (layout.itemAt(i).widget() for i in range(layout.count()))

    @abstractmethod
    def iterable_layout(self) -> QLayout:
        ...
