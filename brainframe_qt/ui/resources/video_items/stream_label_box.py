from PyQt5.QtCore import QPoint, QPointF
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsTextItem

from .stream_polygon import StreamPolygon


class StreamLabelBox(StreamPolygon):
    """This is a textbox that is intended to look pretty and go on top of
    detection or zone objects
    """
    def __init__(self, title_text, top_left, text_size, parent=None):

        # Create the text item
        self.label_text = QGraphicsTextItem(title_text, parent=parent)
        self.label_text.setPos(QPoint(int(top_left[0]), int(top_left[1])))
        self.label_text.setDefaultTextColor(QColor(255, 255, 255))

        font = self.label_text.font()
        font.setPointSizeF(text_size)
        self.label_text.setFont(font)

        rect = self.label_text.sceneBoundingRect().getCoords()
        coords = [QPointF(rect[0], rect[1]),
                  QPointF(rect[2], rect[1]),
                  QPointF(rect[2], rect[3]),
                  QPointF(rect[0], rect[3])]

        super().__init__(points=coords,
                         border_color=parent.pen().color(),
                         fill_color=parent.pen().color(),
                         border_thickness=1,
                         opacity=0.35,
                         parent=parent)

        self.label_text.setZValue(self.zValue() + 1)
        self.label_text.adjustSize()
