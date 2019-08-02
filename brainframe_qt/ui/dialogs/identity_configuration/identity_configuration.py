from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QDialog, QLineEdit, QProgressBar
from PyQt5.uic import loadUi

from brainframe.client.ui.resources.paths import qt_ui_paths
from brainframe.client.ui.resources.ui_elements.buttons import \
    FloatingActionButton
from brainframe.client.ui.resources.ui_elements.containers import Paginator

from .identity_info import IdentityInfo
from .identity_search_filter import IdentitySearchFilter
from .identity_adder_worker import AddNewIdentitiesWorker


class IdentityConfiguration(QDialog):
    display_new_identity_signal = pyqtSignal(object)
    """Emitted when we want to add/display a new Identity on the IdentityGrid
    
    Connected to:
    - IdentityAdderWorker --> Dynamic
    self.identity_adder.identity_uploaded_signal
    - IdentityGridPaginator <-- QtDesigner
    self.identity_grid_paginator.add_new_identities_slot
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.identity_configuration_ui, self)

        self.identity_info: IdentityInfo
        self.identity_search_filter: IdentitySearchFilter
        self.identity_upload_progress_bar: QProgressBar
        self.identity_load_progress_bar: QProgressBar
        self.identity_grid_paginator: Paginator
        self.fab: FloatingActionButton = None

        # Identity Uploader
        self.identity_adder = AddNewIdentitiesWorker(self)
        # noinspection PyUnresolvedReferences
        self.identity_adder.started.connect(
            lambda: self.show_progress_bar(self.identity_upload_progress_bar))
        self.identity_adder.identity_upload_progress_signal.connect(
            lambda current, max_: self.update_progress_bar(
                self.identity_upload_progress_bar, current, max_))
        # noinspection PyUnresolvedReferences
        self.identity_adder.finished.connect(
            lambda: self.hide_progress_bar(self.identity_upload_progress_bar))
        # noinspection PyUnresolvedReferences
        self.identity_adder.finished.connect(
            lambda: self.identity_grid_paginator.set_current_page(0))

        # Identity Loader
        self.identity_grid_paginator.identity_load_started_signal.connect(
            lambda: self.show_progress_bar(self.identity_load_progress_bar))
        self.identity_grid_paginator.identity_load_progress_signal.connect(
            lambda current, max_: self.update_progress_bar(
                self.identity_load_progress_bar, current, max_))
        self.identity_grid_paginator.identity_load_finished_signal.connect(
            lambda: self.hide_progress_bar(self.identity_load_progress_bar))

        self.init_ui()

    @classmethod
    def show_dialog(cls, parent):
        dialog = cls(parent)
        dialog.exec_()

    def init_ui(self):
        self.setWindowFlags(Qt.Window)

        self.identity_info: IdentityInfo
        self.identity_search_filter: IdentitySearchFilter

        self.init_theming()
        self.init_fab()

        self.identity_info.hide()
        self.identity_load_progress_bar.hide()
        self.identity_upload_progress_bar.hide()

    def init_fab(self):
        self.fab = FloatingActionButton(self.identity_grid_paginator,
                                        self.palette().highlight().color())
        # noinspection PyUnresolvedReferences
        self.fab.clicked.connect(self.identity_adder.add_identities_from_file)

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

    # noinspection PyMethodMayBeStatic
    def show_progress_bar(self, progress_bar: QProgressBar):
        progress_bar.show()
        progress_bar.setValue(0)

    # noinspection PyMethodMayBeStatic
    def update_progress_bar(self, progress_bar: QProgressBar,
                            current: int, max_: int):
        progress_bar.show()
        progress_bar.setValue(current)
        progress_bar.setMaximum(max_)

    # noinspection PyMethodMayBeStatic
    def hide_progress_bar(self, progress_bar: QProgressBar):
        progress_bar.hide()
        progress_bar.setValue(0)
