from typing import Optional

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QFont, QFontMetrics
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem

from brainframe_qt.ui.resources.ui_elements.constants import \
    QColorConstants
from .video_item import VideoItem


class LabelItem(VideoItem):
    TEXT_COLOR = QColorConstants.White
    BACKGROUND_OPACITY = 0.35

    def __init__(self, text: str, position: VideoItem.PointType,
                 *, parent: VideoItem, color: QColor = QColorConstants.Black,
                 max_width: Optional[int] = None):
        super().__init__(parent)

        self._text = text
        self.max_width = max_width
        self.background_color = color

        self.text_item = self._init_text_item()
        self.background_box_item = self._init_background_box_item()

        self.setPos(QPointF(*position))

    def _init_text_item(self):
        text_item = QGraphicsTextItem(self.formatted_text, parent=self)
        text_item.setDefaultTextColor(self.TEXT_COLOR)

        return text_item

    def _init_background_box_item(self):
        # TODO: Abstract
        rect = self.text_item.boundingRect()
        background_box_item = QGraphicsRectItem(rect, parent=self)

        brush = background_box_item.brush()
        brush.setColor(self.background_color)
        brush.setStyle(Qt.SolidPattern)
        background_box_item.setBrush(brush)

        pen = background_box_item.pen()
        pen.setColor(self.background_color)
        background_box_item.setPen(pen)

        background_box_item.setOpacity(self.BACKGROUND_OPACITY)

        # Force background behind text_item
        background_box_item.stackBefore(self.text_item)

        return background_box_item

    @property
    def formatted_text(self) -> str:
        text = self._text

        if self.max_width is not None:
            metric = QFontMetrics(QFont())
            text = "\n".join(
                metric.elidedText(line, Qt.ElideRight, self.max_width)
                for line in text.split("\n")
            )

        return text

    @property
    def raw_text(self) -> str:
        return self._text
