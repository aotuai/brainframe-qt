from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QLinearGradient, QPainter, QPaintEvent

from . import FloatingCircleButton


class FloatingActionButton(FloatingCircleButton):
    def __init__(self, parent, radius=28,
                 alignment=Qt.AlignBottom | Qt.AlignRight,
                 m_left=0, m_top=0, m_right=28, m_bottom=28):
        super().__init__(parent, radius, alignment,
                         m_left, m_top, m_right, m_bottom)

    def paintEvent(self, paint_event: QPaintEvent):
        super().paintEvent(paint_event)

        # self._draw_shadow(painter)
        self._draw_plus()

    def _draw_plus(self):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = Qt.NoPen
        painter.setPen(pen)

        palette = self.palette()
        brush = palette.window()
        painter.setBrush(brush)

        rect_width = self.radius / 5
        rect_length = self.radius

        m_left, m_top, _, _ = self.getContentsMargins()
        center_x, center_y = self.radius + m_left, self.radius + m_top

        painter.drawRect(center_x - (rect_width / 2),
                         center_y - (rect_length / 2),
                         rect_width, rect_length)
        painter.drawRect(center_x - (rect_length / 2),
                         center_y - (rect_width / 2),
                         rect_length, rect_width)

    # TODO: Make this work?
    def _draw_shadow(self, painter: QPainter):
        palette = self.palette()
        gradient = QLinearGradient(self.radius, 0, self.radius, self.radius)
        gradient.setColorAt(0, palette.shadow().color())
        gradient.setColorAt(.95, palette.shadow().color())
        gradient.setColorAt(1, Qt.transparent)
        brush = QBrush(gradient)
        painter.setBrush(brush)
        painter.drawEllipse(5, 5, self.radius, self.radius)
