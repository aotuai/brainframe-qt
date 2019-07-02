from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPaintEvent, QPainter, QPen

from . import FloatingCircleButton


class FloatingXButton(FloatingCircleButton):
    def __init__(self, parent, color, radius=10,
                 alignment=Qt.AlignTop | Qt.AlignRight,
                 m_left=0, m_top=0, m_right=0, m_bottom=0):
        super().__init__(parent, radius, alignment, color,
                         m_left, m_top, m_right, m_bottom)

    def paintEvent(self, paint_event: QPaintEvent):
        super().paintEvent(paint_event)

        self._draw_x()

    def _draw_x(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        palette = self.palette()
        brush = palette.alternateBase()
        painter.setBrush(brush)

        rect_width = self.radius / 5
        rect_length = self.radius

        m_left, m_top, _, _ = self.getContentsMargins()
        center_x, center_y = self.radius + m_left, self.radius + m_top

        painter.translate(center_x, center_y)
        painter.rotate(45)

        pen = QPen(brush, rect_width)
        painter.setPen(pen)
        painter.drawLine(QPointF(0, -rect_length / 2),
                         QPointF(0, rect_length / 2))
        painter.drawLine(QPointF(-rect_length / 2, 0),
                         QPointF(rect_length / 2, 0))
