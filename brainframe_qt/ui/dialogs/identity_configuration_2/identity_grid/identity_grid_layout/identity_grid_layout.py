from typing import List

from PyQt5.QtCore import QRect, Qt, QSize
from PyQt5.QtWidgets import QWidget, QGridLayout


class IdentityGridLayout(QGridLayout):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.widgets: List[QWidget] = []
        self.num_cols = 1

    def addWidget(self, widget: QWidget):
        self.widgets.append(widget)

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

    def update_grid(self):
        # Remove all items from layout
        for index in reversed(range(self.count())):
            self.takeAt(index)

        # Add them back, after calculating proper number of columns
        for index, widget in enumerate(self.widgets):
            row, col = divmod(index, self.num_cols)
            super().addWidget(widget, row, col, Qt.AlignCenter)

    def sizeHint(self) -> QSize:

        return self.minimumSize()

    def minimumSize(self) -> QSize:
        """
        The flow layout example added the margins, using a deprecated property.
        The documentation for QLayout.minimumSize says that it shouldn't
        include the space required by self.setContentsMargins. I'm guessing
        adding the margin space was made unnecessary, so I removed it here
        """
        min_width = 0
        for widget in self.widgets:
            min_width = max(min_width, widget.minimumSize().width())

        return QSize(min_width, super().sizeHint().height())
