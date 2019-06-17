from typing import List, Optional

from PyQt5.QtCore import QRect, Qt, QSize, QPoint
from PyQt5.QtWidgets import QWidget, QLayout, QLayoutItem, QStyle, QSizePolicy


class IdentityGridLayout(QLayout):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.items: List[QLayoutItem] = []

        # TODO: I really don't think this works properly
        self.aligned_items = 0
        self.num_cols = 1

        self.min_widget_size = QSize()
        self._calc_min_widget_size()

        self.width = 0
        self.need_redraw = False

    def addItem(self, item: QLayoutItem):
        self.items.append(item)
        item.setAlignment(Qt.AlignCenter)
        self.min_widget_size = self.min_widget_size.expandedTo(
            item.widget().sizeHint())

    def count(self) -> int:
        return len(self.items)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:

        # Naive implementation. Num cols is just how many times we can fit
        # widest widget
        widget_width = self.min_widget_size.width()
        num_cols = width // widget_width if widget_width > 0 else 1

        num_rows = len(self.items) // num_cols
        y_spacing = self.verticalSpacing()
        row_height = self.min_widget_size.height()

        return (num_rows * row_height) + (num_rows - 1 * y_spacing)

    def spacing(self) -> int:
        return -1

    def itemAt(self, index: int) -> Optional[QLayoutItem]:
        try:
            return self.items[index]
        except IndexError:
            # Must return equiv of nullptr if index out of bounds
            return None

    def setGeometry(self, rect: QRect):
        if rect.width() != self.width:
            self.width = rect.width()
            self.need_redraw = True
        if rect != self.geometry():
            self.do_layout(rect)
            super().setGeometry(rect)

    def takeAt(self, index: int) -> QLayoutItem:
        item = self.items.pop(index)
        self._calc_min_widget_size()

        self.need_redraw = True

        return item

    # noinspection PyPep8Naming
    def horizontalSpacing(self) -> int:
        return self.smartSpacing(QStyle.PM_LayoutHorizontalSpacing)

    # noinspection PyPep8Naming
    def verticalSpacing(self) -> int:
        return self.smartSpacing(QStyle.PM_LayoutVerticalSpacing)

    # noinspection PyPep8Naming
    def smartSpacing(self, pm: QStyle.PixelMetric) -> int:
        if not self.parent():
            return -1
        if self.parent().isWidgetType():
            # noinspection PyCallByClass
            parent_as_widget = QWidget.style(self.parent())
            return parent_as_widget.pixelMetric(pm, None, self.parent())
        return self.spacing()

    def do_layout(self, rect: QRect):

        m_left, m_top, m_right, m_bottom = self.getContentsMargins()
        rect.adjust(+m_left, +m_right, -m_right, -m_bottom)

        # Naive implementation. Num cols is just how many times we can fit
        # widest widget
        widget_width = self.min_widget_size.width()
        num_cols = rect.width() // widget_width if widget_width > 0 else 1

        # Ensure that we have at least 1 column
        num_cols = max(1, num_cols)

        if num_cols != self.num_cols:
            # We need to redraw
            # self.aligned_items = 0
            self.num_cols = num_cols
            self.need_redraw = True

        if self.need_redraw:
            self.aligned_items = 0
            self.need_redraw = False

        if self.aligned_items < len(self.items):

            row_height = self.min_widget_size.height()
            h_spacing = self.horizontalSpacing()
            y_spacing = self.verticalSpacing()

            total_h_spacing = (self.num_cols - 1) * h_spacing
            col_width = (rect.width() - total_h_spacing) // self.num_cols

            index = 0
            for index, item in enumerate(self.items[self.aligned_items:],
                                         start=self.aligned_items):

                current_row, current_col = divmod(index, self.num_cols)

                # Force widgets to the left if there's not enough to fill a row
                if len(self.items) < self.num_cols:
                    x = m_left + current_col * (widget_width + h_spacing)
                else:
                    x = m_left + current_col * (col_width + h_spacing)
                y = m_top + current_row * (row_height + y_spacing)

                item.setGeometry(QRect(x, y, col_width, row_height))

            self.aligned_items = index

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        min_width = self.min_widget_size.width()

        if self.items:
            # Docs recommend avoiding using QRect.bottom
            geometry = self.items[-1].geometry()
            min_height = geometry.y() + geometry.height()
        else:
            min_height = super().minimumSize().height()

        m_left, m_top, m_right, m_bottom = self.getContentsMargins()

        # Add contents margins
        min_width += m_left + m_right
        min_height += m_top + m_bottom

        return QSize(min_width, min_height)

    def _calc_min_widget_size(self):
        self.min_widget_size = super().minimumSize()
        for item in self.items:
            self.min_widget_size.expandedTo(item.minimumSize())
