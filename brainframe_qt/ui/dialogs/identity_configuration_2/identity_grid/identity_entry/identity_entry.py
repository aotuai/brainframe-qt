from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QMouseEvent, QPixmap, QPalette
from PyQt5.QtWidgets import QLabel
from PyQt5.uic import loadUiType

from brainframe.client.api.codecs import Identity
from brainframe.client.ui.resources.paths import qt_ui_paths, image_paths

# Preload & parse the UI file into memory, for performance reasons
_Form, _Base = loadUiType(qt_ui_paths.identity_entry_ui)


class IdentityEntry(_Form, _Base):
    identity_clicked_signal = pyqtSignal(object)

    def __new__(cls, *args, **kwargs):
        cls.icon = QPixmap(str(image_paths.person_icon))
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, identity: Identity, parent=None):
        super().__init__(parent=parent)

        self.setupUi(self)

        self.identity_image: QLabel
        self.identity_unique_name: QLabel
        self.identity_nickname: QLabel

        self.identity: Identity = identity

        self.init_names()

        self.identity_image.setPixmap(self.icon)

    # noinspection PyPep8Naming
    def mouseReleaseEvent(self, event: QMouseEvent):
        # noinspection PyUnresolvedReferences
        self.identity_clicked_signal.emit(self.identity)

    def init_names(self):
        self.identity_unique_name.setText(self.identity.unique_name)

        text = f"({self.identity.nickname})" if self.identity.nickname else ""
        self.identity_nickname.setText(text)
        self.identity_image: QLabel
        self.identity_unique_name: QLabel
        self.identity_nickname: QLabel

        # Make nickname use alt text color from theme
        palette = self.identity_nickname.palette()
        text_color = palette.placeholderText().color()
        palette.setColor(QPalette.WindowText, text_color)
        self.identity_nickname.setPalette(palette)
