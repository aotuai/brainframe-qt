from PyQt5.QtWidgets import QScrollArea


class ThumbnailScrollArea(QScrollArea):
    """ScrollArea that accounts for width of the scrollbars when calculating
    size
    """
    # This class exists if we ever want to override any QScrollBar functions
