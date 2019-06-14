from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QMouseEvent, QPixmap, QPalette, QFontMetrics
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

        label_width = self.maximumWidth()

        self._apply_elided_text(self.identity_unique_name,
                                self.identity.unique_name,
                                label_width)

        self.identity_nickname: QLabel
        text = f"({self.identity.nickname})" if self.identity.nickname else ""
        self._apply_elided_text(self.identity_nickname, text, label_width)

        self.identity_image: QLabel
        self.identity_unique_name: QLabel
        self.identity_nickname: QLabel

        # Make nickname use alt text color from theme
        palette = self.identity_nickname.palette()
        text_color = palette.placeholderText().color()
        palette.setColor(QPalette.WindowText, text_color)
        self.identity_nickname.setPalette(palette)

    @staticmethod
    def _apply_elided_text(label: QLabel, text: str, width: int):
        """Apply text to label eliding so as to not surpass a desired width

        Modeled after
        https://api.kde.org/frameworks/kwidgetsaddons/html/classKSqueezedTextLabel.html#ac87795fc4ddf998331b82f3e061ced1a
        """
        # Elide text from middle to have fixed width
        metric = QFontMetrics(label.font())
        line_width = metric.width(text)

        if line_width > width:
            elided_text = metric.elidedText(text, Qt.ElideMiddle, width)
            label.setText(elided_text)
            label.setToolTip(text)
        else:
            label.setText(text)
            label.setToolTip("")
