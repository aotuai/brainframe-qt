import abc
import sys

# noinspection PyUnresolvedReferences
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QStyle
from PyQt5.uic import loadUi

from brainframe.client.ui.resources.paths import qt_ui_paths
from brainframe.client.ui.resources.ui_elements.buttons import TextIconButton


# Hack to allow class to inherit from both QObject (type=sip.wrappertype) and
# abc.ABC (type=type)
class PaginatorMeta(type(QWidget), type(abc.ABCMeta)):
    pass


class PaginatorClass(QWidget):
    pass


class Paginator(PaginatorClass, metaclass=PaginatorMeta):

    def __init__(self, page_size: int, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.paginator_ui, self)

        self._widget: QWidget = None
        self._page_size: int = page_size

        self.current_page: int = 0
        self.total_items: int = 0

        self._container_widget: QWidget
        self.displaying_label: QLabel
        self.of_label: QLabel
        self.prev_page_button: TextIconButton
        self.next_page_button: TextIconButton

        self.__init_ui()
        self.__init_slots_and_signals()

    def __init_ui(self):
        self.of_label.setContentsMargins(5, 0, 5, 0)

        self.displaying_label: QLabel
        self.displaying_label.setContentsMargins(0, 0, 5, 0)

        self.prev_page_button.setIcon(
            self.style().standardIcon(QStyle.SP_ArrowBack))
        self.next_page_button.setIcon(
            self.style().standardIcon(QStyle.SP_ArrowForward))

        self.prev_page_button: TextIconButton
        self.prev_page_button.setEnabled(True)

    def __init_slots_and_signals(self):
        self.prev_page_button.clicked.connect(self.prev_page)
        self.next_page_button.clicked.connect(self.next_page)

    @property
    def container_widget(self) -> QWidget:
        return self._container_widget

    @container_widget.setter
    def container_widget(self, container_widget: QWidget):
        layout = self.layout()
        if self._container_widget:
            layout.replaceWidget(self._container_widget, container_widget)
            # No idea why deleteLater does not work here
            self._container_widget.setParent(None)
        else:
            layout.addWidget(container_widget)
        # noinspection PyAttributeOutsideInit
        self._container_widget = container_widget

    @pyqtProperty(int)
    def page_size(self) -> int:
        return self._page_size

    @page_size.setter
    def page_size(self, page_size: int):
        self._page_size = page_size

    @property
    def widget(self) -> QWidget:
        return self._widget

    @widget.setter
    def widget(self, widget):
        self._widget = widget

    @pyqtSlot()
    def next_page(self):
        self.current_page += 1
        self.get_page(self.current_page)

    @pyqtSlot()
    def prev_page(self):
        self.current_page -= 1
        self.get_page(self.current_page)

    @abc.abstractmethod
    def get_page(self, page: int):
        raise NotImplementedError


if __name__ == '__main__':
    app = QApplication(sys.argv)

    a = Paginator(100)
    a.show()

    app.exec_()
