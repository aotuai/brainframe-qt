from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QPlainTextEdit, QStyle, \
    QStyleOptionTab, QStylePainter, QTabBar, QTabWidget, QWidget
from PyQt5.uic import loadUi

from brainframe.client.extensions import AboutActivity
from brainframe.client.ui.resources.paths import qt_ui_paths, text_paths


class AboutPageActivity(AboutActivity):
    _built_in = True

    def open(self, *, parent: QWidget):
        return AboutPage.show_dialog(parent=parent)

    def window_title(self) -> str:
        return QApplication.translate("AboutPageActivity", "About BrainFrame")

    @staticmethod
    def icon() -> QIcon:
        return QIcon(":/icons/info")

    @staticmethod
    def short_name() -> str:
        return QApplication.translate("AboutPageActivity", "About")


class AboutPage(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.about_page_ui, self)

        self.tab_widget.setTabBar(HorizontalTabBar())

        # Needs to be done after setting TabBar, therefor not in .ui file
        self.tab_widget.setTabPosition(QTabWidget.West)

        for license_ in sorted(text_paths.license_dir.iterdir()):
            # Create text field to display license
            tab = QPlainTextEdit(license_.read_text(encoding="utf8"), self)
            tab.setReadOnly(True)

            # Make text monospace using a fake font with a style hint
            # This lets the system choose its preferred font
            font = QFont("unexistent")
            font.setStyleHint(QFont.Monospace)
            tab.setFont(font)

            # Add text box to tab widget
            self.tab_widget.addTab(tab, license_.suffix[1:])

    @classmethod
    def show_dialog(cls, parent):
        dialog = cls(parent)
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
