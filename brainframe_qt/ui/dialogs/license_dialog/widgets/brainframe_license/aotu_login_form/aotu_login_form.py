from PyQt5.QtCore import QObject, pyqtSignal

from .aotu_login_form_ui import AotuLoginFormUI


class AotuLoginForm(AotuLoginFormUI):
    oath_login_requested = pyqtSignal()

    def __init__(self, *, parent: QObject):
        super().__init__(parent=parent)

        self._init_signals()

    def _init_signals(self) -> None:
        self.oauth_button.clicked.connect(self.oath_login_requested)
