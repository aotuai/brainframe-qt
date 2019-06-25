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
class PaginatorMeta(type(QWidget), type(abc.ABC)):
    pass


class Paginator(QWidget, metaclass=PaginatorMeta):

    def __init__(self, page_size: int, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.paginator_ui, self)

        self._page_size: int = page_size
        self.current_page: int = 0
        self._total_items: int = 0

        self.scroll_area_widget: QWidget
        self.range_lower_label: QLabel
        self.range_upper_label: QLabel
        self.item_total_label: QLabel
        self.prev_page_button: TextIconButton
        self.next_page_button: TextIconButton

        self.__init_ui()
        self.__init_slots_and_signals()

    def __init_ui(self):
        self.of_label.setContentsMargins(5, 0, 5, 0)

        self.displaying_label.setContentsMargins(0, 0, 5, 0)

        self.prev_page_button.setIcon(
            self.style().standardIcon(QStyle.SP_ArrowBack))
        self.next_page_button.setIcon(
            self.style().standardIcon(QStyle.SP_ArrowForward))

    def __init_slots_and_signals(self):
        self.prev_page_button.clicked.connect(self.prev_page)
        self.next_page_button.clicked.connect(self.next_page)

    @abc.abstractmethod
    def add_item(self, item):
        raise NotImplementedError

    def add_widget(self, widget):
        self.container_layout.addWidget(widget)

    @abc.abstractmethod
    def clear_layout(self):
        raise NotImplementedError

    @property
    def container_layout(self) -> QWidget:
        return self.scroll_area_widget.layout()

    @container_layout.setter
    def container_layout(self, container_layout: QWidget):
        if self.container_layout:
            self.scroll_area_widget.layout().deleteLater()
        self.scroll_area_widget.setLayout(container_layout)

        self.set_current_page(0)

    def set_current_page(self, current_page: int):
        self.current_page = current_page
        self.display_page(self.current_page)

        self.range_lower_label.setText(str(self.range_lower))
        self.range_upper_label.setText(str(self.range_upper))

        self.prev_page_button.setDisabled(self.range_lower <= 1)

    @abc.abstractmethod
    def display_page(self, page: int):
        raise NotImplementedError

    @pyqtSlot()
    def next_page(self):
        self.set_current_page(self.current_page + 1)

    @pyqtSlot()
    def prev_page(self):
        self.set_current_page(self.current_page - 1)

    @pyqtProperty(int)
    def page_size(self) -> int:
        return self._page_size

    @page_size.setter
    def page_size(self, page_size: int):
        self._page_size = page_size
        self.set_current_page(0)

    @property
    def range_lower(self):
        """Inclusive"""
        # noinspection PyPropertyAccess
        page_size = self.page_size
        return self.current_page * page_size + 1

    @property
    def range_upper(self):
        """Inclusive"""
        # noinspection PyPropertyAccess
        page_size = self.page_size
        return min(self.total_items, (self.current_page + 1) * page_size)

    @property
    def total_items(self) -> int:
        return self._total_items

    @total_items.setter
    def total_items(self, total_items: int):
        self._total_items = total_items
        self.item_total_label.setText(str(self._total_items))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    a = Paginator(100)
    a.show()

    app.exec_()
