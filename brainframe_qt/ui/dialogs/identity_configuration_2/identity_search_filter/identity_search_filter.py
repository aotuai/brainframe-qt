from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from brainframe.client.ui.resources.paths import qt_ui_paths


class IdentitySearchFilter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.identity_search_filter_ui, self)
