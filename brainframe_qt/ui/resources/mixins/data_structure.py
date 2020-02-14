from abc import abstractmethod

from PyQt5.QtWidgets import QLayout

from brainframe.client.ui.resources.mixins import BaseMixin


class IterableMI(BaseMixin):

    def __iter__(self):
        layout = self.iterable_layout()
        return (layout.itemAt(i).widget() for i in range(layout.count()))

    @abstractmethod
    def iterable_layout(self) -> QLayout:
        ...
