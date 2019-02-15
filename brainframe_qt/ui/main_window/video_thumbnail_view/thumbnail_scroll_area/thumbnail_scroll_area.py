import sys

from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtWidgets import QScrollArea, QSizePolicy, QStyle, QWidget


class ThumbnailScrollArea(QScrollArea):
    """ScrollArea that accounts for width of the scrollbars when calculating
    size
    """

    def resizeEvent(self, event):

        viewport_height = self.viewport().height()
        widget_height = self.widget().height()

        # 36 is a magic number
        if widget_height > viewport_height + 36:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        super().resizeEvent(event)
