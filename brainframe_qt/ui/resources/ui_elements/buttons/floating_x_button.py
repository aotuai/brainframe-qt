from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPaintEvent, QPainter, QTransform

from . import FloatingCircleButton


class FloatingXButton(FloatingCircleButton):
    def __init__(self, parent, radius=10,
                 alignment=Qt.AlignTop | Qt.AlignRight,
                 m_left=0, m_top=0, m_right=0, m_bottom=0):
        super().__init__(parent, radius, alignment,
                         m_left, m_top, m_right, m_bottom)

    def paintEvent(self, paint_event: QPaintEvent):
        super().paintEvent(paint_event)

        self._draw_x()

    def _draw_x(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = Qt.NoPen
        painter.setPen(pen)

        palette = self.palette()
        brush = palette.linkVisited()
        painter.setBrush(brush)

        rect_width = self.radius / 6
        rect_length = self.radius

        m_left, m_top, _, _ = self.getContentsMargins()
        center_x, center_y = self.radius + m_left, self.radius + m_top

        rect1 = QRect(center_x - (rect_width / 2),
                      center_y - (rect_length / 2),
                      rect_width, rect_length)

        rect1 = QTransform().rotate(45).mapRect(rect1)

        painter.drawRect(rect1)
        painter.drawRect(center_x - (rect_length / 2),
                         center_y - (rect_width / 2),
                         rect_length, rect_width)
