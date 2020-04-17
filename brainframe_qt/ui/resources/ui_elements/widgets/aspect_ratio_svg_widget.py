from typing import Union

from PyQt5.QtCore import QPointF, QRectF, QSize, QSizeF, Qt
from PyQt5.QtGui import QPaintEvent, QPainter
from PyQt5.QtSvg import QSvgWidget


class AspectRatioSVGWidget(QSvgWidget):

    def __init__(self, *args):
        super().__init__(*args)

        self._alignment: Qt.AlignmentFlag = Qt.AlignCenter

    def paintEvent(self, paint_event: QPaintEvent):
        painter = QPainter(self)

        svg_size = QSizeF(self.renderer().defaultSize())
        widget_size = QSizeF(self.size())

        new_size = svg_size.scaled(widget_size, Qt.KeepAspectRatio)
        offset = self._get_offset(new_size, widget_size)

        bounds = QRectF(offset, new_size)
        self.renderer().render(painter, bounds)

    @property
    def alignment(self) -> Qt.AlignmentFlag:
        return self._alignment

    @alignment.setter
    def alignment(self, alignment: Qt.AlignmentFlag):
        self._alignment = alignment
        self.repaint()

    def _get_offset(self, image_size: Union[QSize, QSizeF],
                    widget_size: Union[QSize, QSizeF]) \
            -> QPointF:
        x_offset = 0
        y_offset = 0

        if self.alignment & Qt.AlignLeft:
            x_offset = 0
        if self.alignment & Qt.AlignHCenter:
            x_offset = (widget_size.width() - image_size.width()) / 2
        if self.alignment & Qt.AlignRight:
            x_offset = widget_size.width() - image_size.width()

        if self.alignment & Qt.AlignTop:
            y_offset = 0
        if self.alignment & Qt.AlignVCenter:
            y_offset = (widget_size.height() - image_size.height()) / 2
        if self.alignment & Qt.AlignBottom:
            y_offset = widget_size.height() - image_size.height()

        return QPointF(x_offset, y_offset)
