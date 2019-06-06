from typing import List

from PyQt5.QtCore import QRect, Qt, QSize
from PyQt5.QtWidgets import QWidget, QGridLayout, QLayoutItem, QSpacerItem, \
    QSizePolicy


class IdentityGridLayout(QGridLayout):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.widgets: List[QWidget] = []
        self.num_cols = 1

    def addWidget(self, widget: QWidget):
        self.widgets.append(widget)
        self.update_grid()

    def setGeometry(self, rect: QRect):
        super().setGeometry(rect)

        if not self.widgets:
            return

        # Naive implementation. Num cols is just how many times we can fit
        # widest widget
        widget_widths = (widget.sizeHint().width() for widget in self.widgets)
        max_widget_width = max(widget_widths)
        num_cols = rect.width() // max_widget_width

        # Ensure that we have at least 1 column
        num_cols = max(1, num_cols)

        if self.num_cols != num_cols:
            self.num_cols = num_cols
            self.update_grid()

    def takeAt(self, index: int) -> QLayoutItem:
        item = super().takeAt(index)
        widget = item.widget()
        self.widgets.remove(widget)
        return item

    def update_grid(self):
        # Remove all items from layout
        for index in reversed(range(self.count())):
            super().takeAt(index)

        # Add them back, after calculating proper number of columns
        for index, widget in enumerate(self.widgets):
            row, col = divmod(index, self.num_cols)
            super().addWidget(widget, row, col, Qt.AlignCenter)

    def sizeHint(self) -> QSize:

        return self.minimumSize()

    def minimumSize(self) -> QSize:
        """For whatever reason this is needed to let the layout shrink down to
        1 column wide.
        """
        min_width = min(self.widgets,
                        key=lambda w: w.sizeHint().width(),
                        default=super()).width()

        return QSize(min_width, super().sizeHint().height())
