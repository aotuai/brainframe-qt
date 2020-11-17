from abc import ABC, abstractmethod

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget


class ClientActivity(ABC):
    _built_in = False

    @staticmethod
    @abstractmethod
    def icon() -> QIcon:
        ...

    @staticmethod
    @abstractmethod
    def short_name() -> str:
        """Used as the text on the QAction in the Toolbar"""
        ...


class WindowedActivity(ClientActivity, ABC):

    @staticmethod
    @abstractmethod
    def main_widget(*, parent: QWidget) -> QWidget:
        ...

    def on_show(self):
        pass

    def on_hide(self):
        pass


class DialogActivity(ClientActivity, ABC):
    is_modal: bool = True

    @abstractmethod
    def open(self, *, parent: QWidget):
        ...

    @abstractmethod
    def window_title(self) -> str:
        return ""


class AboutActivity(DialogActivity, ABC):
    """Only to be used by the built-in About Page activity"""
    pass
