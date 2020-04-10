from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QStackedWidget, QWidget

from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.ui_elements.widgets import LabeledIcon


class _VerticalTabbingWidgetUI(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QVBoxLayout()

        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)


class _VerticalTabbingWidget(_VerticalTabbingWidgetUI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

    def add_tab(self, tab_name: str, icon: QIcon) -> LabeledIcon:
        tab_widget = LabeledIcon(tab_name, icon, self)
        self.layout().addWidget(tab_widget)

        return tab_widget


class _StackedTabWidgetUI(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.tabbing_widget = self._init_tabbing_widget()
        self.stacked_widget = self._init_stacked_widget()

        self._init_layout()
        self._init_style()

    def _init_tabbing_widget(self) -> _VerticalTabbingWidget:
        tabbing_widget = _VerticalTabbingWidget(self)
        return tabbing_widget

    def _init_stacked_widget(self) -> QStackedWidget:
        stacked_widget = QStackedWidget(self)
        return stacked_widget

    def _init_layout(self) -> None:
        layout = QHBoxLayout()

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(0)

        layout.addWidget(self.tabbing_widget)
        layout.addWidget(self.stacked_widget)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.stacked_tab_widget_qss)


class StackedTabWidget(_StackedTabWidgetUI):
    """This is used instead of a QTabWidget because we want custom tabs, on the
    left of the tab widget, with custom QSS styling. There is no good way to
    use a QTabWidget with QSS and have the tabs on the left. This also makes
    it easier to create custom tabs"""

    def __init__(self, parent: QWidget):
        super().__init__(parent)

    def add_widget(self, widget: QWidget, tab_name: str, icon: QIcon) -> None:
        tab_widget = self.tabbing_widget.add_tab(tab_name, icon)
        self.stacked_widget.addWidget(widget)

        tab_widget.clicked.connect(
            lambda: self.stacked_widget.setCurrentWidget(widget))

    def remove_widget(self, widget: QWidget):
        raise NotImplementedError


if __name__ == '__main__':
    import typing

    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QApplication, QDesktopWidget, QVBoxLayout, \
        QPushButton

    from brainframe.client.ui.resources.paths import image_paths, qt_qss_paths

    # noinspection PyArgumentList
    app = QApplication([])

    # noinspection PyArgumentList
    window = QWidget()
    window.setWindowFlags(Qt.WindowStaysOnTopHint)
    window.resize(QDesktopWidget().availableGeometry(window).size() * .4)
    window.setAttribute(Qt.WA_StyledBackground, True)

    layout = QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)

    window.setLayout(layout)
    stacked_tab_widget = StackedTabWidget(typing.cast(QWidget, None))
    window.layout().addWidget(stacked_tab_widget)

    q_icon = QIcon(str(image_paths.question_mark_icon))
    stacked_tab_widget.add_widget(QPushButton("1"), "Streams", q_icon)
    stacked_tab_widget.add_widget(QPushButton("2"), "Tasks", q_icon)
    stacked_tab_widget.add_widget(QPushButton("3"), "Identities", q_icon)
    stacked_tab_widget.add_widget(QPushButton("4"), "Settings", q_icon)

    window.show()
    app.exec_()
