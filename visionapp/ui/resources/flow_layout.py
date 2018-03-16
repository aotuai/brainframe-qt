from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.QtWidgets import QLayout, QSizePolicy


class FlowLayout(QLayout):

    def __init__(self, parent=None, margin=0, spacing=-1):

        super().__init__(parent)

        if parent:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)

        self.items = []

    def __del__(self):
        while self.takeAt(0):
            pass

    def addItem(self, item):
        """Add item to layout"""
        self.items.append(item)

    def count(self):
        """Number of items in layout"""
        return len(self.items)

    def itemAt(self, index):
        """Peek item at index in layout"""
        if 0 <= index < len(self.items):
            return self.items[index]

        return None

    def takeAt(self, index):
        """Pop item at index in layout"""
        if 0 <= index < len(self.items):
            return self.items.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._apply_layout(QRect(0, 0, width, 0), apply=False)

    def setGeometry(self, rect: QRect):
        """Set geometry to rect"""
        super().setGeometry(rect)
        self._apply_layout(rect, apply=True)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self.items:
            size = size.expandedTo(item.sizeHint())

        size += QSize(2 * self._get_margins(), 2 * self._get_margins())

        return size

    def _get_margins(self):
        return self.getContentsMargins()[0]

    def _apply_layout(self, rect, apply=True):

        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(+left, +top, -right, -bottom)

        x, y = effective_rect.x(), effective_rect.y()
        line_height = 0

        for item in self.items:

            widget = item.widget()

            space_x = self.spacing() + widget.style().layoutSpacing(
                QSizePolicy.DefaultType,
                QSizePolicy.DefaultType,
                Qt.Horizontal
            )

            space_y = self.spacing() + widget.style().layoutSpacing(
                QSizePolicy.DefaultType,
                QSizePolicy.DefaultType,
                Qt.Vertical
            )

            next_x = x + item.sizeHint().width() + space_x
            if (next_x - space_x > effective_rect.right()) and line_height > 0:
                x = effective_rect.x()
                y += line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if apply:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()



