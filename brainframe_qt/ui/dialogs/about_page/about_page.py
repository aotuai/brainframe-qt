from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QPlainTextEdit,
    QStyle,
    QStyleOptionTab,
    QStylePainter,
    QTabBar,
    QTabWidget
)
from PyQt5.uic import loadUi

from brainframe.client.ui.resources.paths import qt_ui_paths, text_paths


class AboutPage(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.about_page_ui, self)

        self.tab_widget.setTabBar(HorizontalTabBar())

        # Needs to be done after setting TabBar, therefor not in .ui file
        self.tab_widget.setTabPosition(QTabWidget.West)

        for license_ in sorted(text_paths.license_dir.iterdir()):
            tab = QPlainTextEdit(license_.read_text(), self)
            self.tab_widget.addTab(tab, license_.suffix[1:])

    @classmethod
    def show_dialog(cls):

        dialog = cls()
        dialog.exec_()


class HorizontalTabBar(QTabBar):

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(option, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, option)
            painter.drawText(self.tabRect(i),
                             Qt.AlignCenter | Qt.TextDontClip,
                             self.tabText(i))

    def tabSizeHint(self, index: int):

        size = QTabBar.tabSizeHint(self, index)
        if size.width() < size.height():
            size.transpose()
        return size
