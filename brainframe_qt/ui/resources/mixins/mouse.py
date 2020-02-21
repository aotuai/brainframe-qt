from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor, QMouseEvent

from brainframe.client.ui.resources.mixins import BaseMixin


class ClickableMI(BaseMixin):

    def __init_subclass__(cls, **kwargs):
        """This is required because of the magic PyQt does to signals.
        If clicked is simply declared as an attribute of the base mixin class,
        PyQt will be unable to connect the signal from a subclass. Not really
        sure why, but this works.
        """
        cls.clicked = pyqtSignal()
        super().__init_subclass__(**kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Emit a signal when the widget is clicked"""
        if event.button() != Qt.LeftButton:
            return

        # Mouse release events are triggered on the Widget where the mouse was
        # initially pressed. If the user presses the mouse down, moves the
        # cursor off the widget, and then releases the button, we want to
        # ignore it.
        if not self.rect().contains(event.pos()):
            return

        # noinspection PyUnresolvedReferences
        self.clicked.emit()
