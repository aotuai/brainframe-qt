from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QBrush, QLinearGradient, QPainter, QPaintEvent

from . import FloatingCircleButton


class FloatingActionButton(FloatingCircleButton):
    def __init__(self, parent, radius,
                 alignment=Qt.AlignBottom | Qt.AlignRight,
                 m_left=28, m_top=28, m_right=28, m_bottom=28):
        super().__init__(parent, radius, alignment,
                         m_left, m_top, m_right, m_bottom)

    def paintEvent(self, paint_event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = Qt.NoPen
        painter.setPen(pen)

        # self._draw_shadow(painter)
        self._draw_button(painter)
        self._draw_plus(painter)

    def _draw_button(self, painter: QPainter):
        palette = self.palette()
        # I have no clue why isDown needs to be flipped here
        brush = palette.text() if not self.isDown() else palette.shadow()
        painter.setBrush(brush)

        m_left, m_top, _, _ = self.getContentsMargins()
        painter.drawEllipse(QPoint(self.radius + m_left, self.radius + m_top),
                            self.radius, self.radius)

    def _draw_plus(self, painter: QPainter):
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
