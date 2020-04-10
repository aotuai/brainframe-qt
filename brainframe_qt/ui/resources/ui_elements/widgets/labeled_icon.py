from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.mixins.mouse import ClickableMI
from brainframe.client.ui.resources.paths import qt_qss_paths
from brainframe.client.ui.resources.ui_elements.widgets import ImageLabel


class _LabeledIconUI(QWidget):
    MAX_ICON_SIZE = QSize(128, 128)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.icon_widget = self._init_icon_widget()
        self.tab_name_label = self._init_tab_name_label()

        self._init_layout()
        self._init_style()

    def _init_icon_widget(self) -> ImageLabel:
        icon_widget = ImageLabel(self)
        icon_widget.has_height_for_width = False

        # TODO: placeholder icon
        icon_widget.pixmap_ = QIcon().pixmap(1, 1)
        return icon_widget

    def _init_tab_name_label(self) -> QLabel:
        tab_name_label = QLabel("[Tab Name]", self)

        return tab_name_label

    def _init_layout(self) -> None:
        layout = QVBoxLayout()

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(self.icon_widget, Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.tab_name_label, Qt.AlignCenter)

        self.setLayout(layout)

    def _init_style(self):
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        # self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        stylesheet_watcher.watch(self, qt_qss_paths.labeled_icon_qss)


class LabeledIcon(_LabeledIconUI, ClickableMI):

    def __init__(self, tab_name: str, icon: QIcon, parent: QWidget):
        super().__init__(parent)

        self.tab_name = tab_name
        self.icon = icon

    @property
    def tab_name(self) -> str:
        return self.tab_name_label.text()

    @tab_name.setter
    def tab_name(self, tab_name: str) -> None:
        self.tab_name_label.setText(tab_name)

    @property
    def icon(self) -> QIcon:
        # Only setter
        raise NotImplementedError

    @icon.setter
    def icon(self, icon: QIcon) -> None:
        self.icon_widget.pixmap_ = icon.pixmap(self.MAX_ICON_SIZE)
