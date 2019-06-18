import math

from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QBrush, QLinearGradient, QPainter, QPaintEvent, \
    QMouseEvent, QRegion, QResizeEvent

from . import FloatingButton


class FloatingActionButton(FloatingButton):
    def __init__(self, parent, radius=28,
                 alignment=Qt.AlignBottom | Qt.AlignRight,
                 m_left=28, m_top=28, m_right=28, m_bottom=28):
        super().__init__(alignment, parent=parent)

        self.radius = radius

        size = QSize(self.radius * 2, self.radius * 2)
        size += QSize(m_left + m_right, m_top + m_bottom)
        self.resize(size)

        self.setContentsMargins(m_left, m_top, m_right, m_bottom)

        self.parent().installEventFilter(self)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """On resize we need to adjust the mask to fit around the button circle

        This allows mouse presses to pass through to widgets behind if they're
        not on the button, but within the space of the widget's rect (ie.
        the corner)

        This also means we do not need to override buttonHit because we can
        only click on the button if it's within the mask
        """
        # Remove margins
        m_left, m_top, m_right, m_bottom = self.getContentsMargins()
        button_rect = self.rect().adjusted(m_left, m_top, -m_right, -m_bottom)

        # Add some extra pixels for anti-aliasing
        button_rect.adjust(-1, -1, 1, 1)
        self.setMask(QRegion(button_rect, QRegion.Ellipse))
        super().resizeEvent(event)

    def paintEvent(self, paint_event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = Qt.NoPen
        painter.setPen(pen)

        # self._draw_shadow(painter)
        self._draw_button(painter)
        self._draw_plus(painter)

    def mousePressEvent(self, event: QMouseEvent):
        print(event.pos())
        print(self.hitButton(event.pos()))
        super().mousePressEvent(event)

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
