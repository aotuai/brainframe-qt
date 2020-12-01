from PyQt5.QtCore import QEvent, Qt, pyqtSignal
from PyQt5.QtGui import QFontMetrics, QMouseEvent, QPaintEvent, QPalette, \
    QPixmap
from PyQt5.QtWidgets import QLabel, QStyle, QStyleOption
from PyQt5.uic import loadUiType

from brainframe.api.bf_codecs import Identity
# noinspection PyUnresolvedReferences
from brainframe_qt.ui.resources import qt_resources
from brainframe_qt.ui.resources.paths import qt_ui_paths
from brainframe_qt.ui.resources.ui_elements.buttons import FloatingXButton

# Preload & parse the UI file into memory, for performance reasons
_Form, _Base = loadUiType(qt_ui_paths.identity_entry_ui)


class IdentityEntry(_Form, _Base):
    identity_clicked_signal = pyqtSignal(object, bool)
    """Emitted whenever the body of the widget is clicked
    
    Connected to:
    - IdentityGridPaginator <-- Dynamic
      [parent].identity_clicked_slot
    """
    identity_delete_signal = pyqtSignal(object)
    """Emitted whenever the delete button is clicked
    
    Connected to:
    - FloatingXButton --> Dynamic
      lambda: self.identity_delete_button.clicked
    - IdentityGridPaginator <-- Dynamic
      [parent].delete_identity_slot
    """

    def __new__(cls, *args, **kwargs):
        cls.icon = QPixmap(":/icons/person")
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, identity: Identity, parent=None):
        super().__init__(parent=parent)

        self.setupUi(self)

        self.identity_image: QLabel
        self.identity_unique_name: QLabel
        self.identity_nickname: QLabel

        self.identity_delete_button: FloatingXButton = None

        self.identity: Identity = identity
        self._selected: bool = False

        self._init_ui()
        self._init_names()

        self.identity_image.setPixmap(self.icon)

    def _init_names(self):

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
        text_color = palette.mid().color()
        palette.setColor(QPalette.WindowText, text_color)
        self.identity_nickname.setPalette(palette)

    def _init_ui(self):

        self.identity_delete_button = FloatingXButton(
            self, self.palette().mid())
        self.identity_delete_button.hide()

        # noinspection PyUnresolvedReferences
        self.identity_delete_button.clicked.connect(
            lambda: self.identity_delete_signal.emit(self.identity))

    # noinspection PyPep8Naming
    def enterEvent(self, event: QEvent):
        self.identity_delete_button.show()
        super().enterEvent(event)

    # noinspection PyPep8Naming
    def leaveEvent(self, event: QEvent):
        self.identity_delete_button.hide()
        super().leaveEvent(event)

    # noinspection PyPep8Naming
    def mouseReleaseEvent(self, event: QMouseEvent):

        self.selected = not self.selected

        # noinspection PyUnresolvedReferences
        self.identity_clicked_signal.emit(self.identity, self.selected)

    # noinspection PyPep8Naming
    def paintEvent(self, event: QPaintEvent):
        self._update_background_color()

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, selected: bool):
        self._selected = selected
        self.repaint()

    def _update_background_color(self):
        option = QStyleOption()
        option.initFrom(self)

        hovered = option.state & QStyle.State_MouseOver

        palette = self.parent().palette()
        if not self.selected and not hovered:
            background_color = palette.window().color()
        elif hovered and not self.selected:
            background_color = palette.alternateBase().color()
        elif self.selected and not hovered:
            background_color = palette.dark().color()
        else:
            background_color = palette.shadow().color()
        palette.setColor(QPalette.Window, background_color)
        self.setPalette(palette)

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
