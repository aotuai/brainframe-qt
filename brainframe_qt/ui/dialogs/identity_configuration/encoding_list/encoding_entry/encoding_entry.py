from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QPalette
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QStyle, \
    QStyleOptionButton
from PyQt5.uic import loadUi

from brainframe.client.ui.resources.paths import qt_ui_paths


class EncodingEntry(QWidget):
    encoding_entry_selected_signal = pyqtSignal(bool, str)
    """Emitted when the widget (excluding delete button) is selected (clicked)

    Only emitted when self.selectable == True

    Connected to:
    - EncodingList <-- Dynamic
      [parent].encoding_entry_selected_slot
    """
    delete_encoding_signal = pyqtSignal(str)
    """Emitted when the delete button is pressed
    
    Connected to:
    - EncodingList <-- Dynamic
    [parent].delete_encoding_signal
    """

    def __init__(self, encoding_class_name: str, parent=None, ):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.encoding_entry_ui, self)

        self.encoding_class_name = encoding_class_name

        self.encoding_class_name_label: QLabel
        self.encoding_class_name_label.setText(self.encoding_class_name)
        self.delete_button: QPushButton

        self.selectable = True
        self._selected = False
        self._hovered = False

        self.init_ui()
        self.init_slots_and_signals()

    def init_ui(self):

        self.delete_button.setToolTip(
            f"Delete all [{self.encoding_class_name}] encodings from the "
            f"database")

        # Set this before hiding the button, as the button is taller than the
        # rest of the widget. Not doing this will make this widget height
        # change when the button is hidden/shown
        self.setMinimumHeight(self.sizeHint().height())
        self.delete_button.hide()

    def init_slots_and_signals(self):
        # noinspection PyUnresolvedReferences
        self.delete_button.clicked.connect(
            lambda: self.delete_encoding_signal.emit(self.encoding_class_name))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.selectable:
            self.selected = not self.selected
            self._update_background_color()

            # noinspection PyUnresolvedReferences
            self.encoding_entry_selected_signal.emit(self.selected,
                                                     self.encoding_class_name)

    def enterEvent(self, event: QEvent):
        self.delete_button.show()
        self.hovered = True

        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        self.delete_button.hide()
        self.hovered = False

        super().leaveEvent(event)

    @property
    def hovered(self):
        return self._hovered

    @hovered.setter
    def hovered(self, hovered):
        self._hovered = hovered
        self._update_background_color()

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, selected):
        self._selected = selected

        self._update_background_color()

    def _update_background_color(self):
        palette = self.parent().palette()
        if not self.selected and not self.hovered:
            background_color = palette.alternateBase().color()
        elif self.hovered and not self.selected:
            background_color = palette.button().color()
        elif self.selected and not self.hovered:
            background_color = palette.dark().color()
        else:
            background_color = palette.shadow().color()
        palette.setColor(QPalette.Background, background_color)
        self.setPalette(palette)
