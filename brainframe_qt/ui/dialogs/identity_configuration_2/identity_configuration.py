from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QDialog, QLineEdit, QScrollArea
from PyQt5.uic import loadUi

from brainframe.client.ui.resources.paths import qt_ui_paths
from brainframe.client.ui.resources.ui_elements.floating_action_button import \
    FloatingActionButton

from .identity_grid import IdentityGrid
from .identity_info import IdentityInfo
from .identity_search_filter import IdentitySearchFilter


class IdentityConfiguration(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.identity_configuration_ui2, self)

        self.identity_grid: IdentityGrid
        self.identity_info: IdentityInfo
        self.identity_search_filter: IdentitySearchFilter
        self.fab: FloatingActionButton = None

        self.init_ui()

    @classmethod
    def show_dialog(cls):
        dialog = cls()
        dialog.exec_()

    def init_ui(self):
        self.identity_info: IdentityInfo
        self.identity_search_filter: IdentitySearchFilter

        self.init_theming()
        self.init_fab()

        self.identity_info.hide()

    def init_fab(self):
        self.identity_grid_area: QScrollArea
        self.fab = FloatingActionButton(28, 25,
                                        self.identity_grid_area.viewport())
        # noinspection PyUnresolvedReferences
        self.fab.clicked.connect(lambda: print("TODO: Add identities"))

    def init_theming(self):
        """Change color palettes"""

        palette = self.identity_search_filter.palette()
        palette.setColor(QPalette.Window, palette.alternateBase().color())
        self.identity_search_filter.setPalette(palette)
        self.identity_search_filter.setAutoFillBackground(True)

        line_edit: QLineEdit = self.identity_search_filter.search_line_edit
        palette = line_edit.palette()
        palette.setColor(QPalette.Base, self.palette().window().color())
        line_edit.setPalette(palette)
        line_edit.setAutoFillBackground(True)

        palette = self.identity_info.palette()
        palette.setColor(QPalette.Window, palette.alternateBase().color())
        self.identity_info.setPalette(palette)
        self.identity_info.setAutoFillBackground(True)
