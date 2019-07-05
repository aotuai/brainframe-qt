from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget


class ThumbnailScrollArea(QScrollArea):
    """ScrollArea that accounts for width of the scrollbars when calculating
    size
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._init_ui()

    def _init_ui(self):
        # Make this widget transparent
        palette = self.palette()
        palette.setColor(palette.Window, Qt.transparent)
        self.setPalette(palette)

    def setWidget(self, widget: QWidget) -> None:
        """Force the inner container widget to be transparent. For whatever
        reason, it's not transparent by default. Using stylesheet doesn't work
        because it affects children"""

        super().setWidget(widget)

        palette = widget.palette()
        palette.setColor(palette.Window, Qt.transparent)
        widget.setPalette(palette)

    def resizeEvent(self, event):

        viewport_height = self.viewport().height()
        widget_height = self.widget().height()

        # 36 is a magic number
        if widget_height > viewport_height + 36:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        super().resizeEvent(event)
