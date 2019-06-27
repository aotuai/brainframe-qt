from PyQt5.QtCore import QSize, QPoint, Qt
from PyQt5.QtGui import QResizeEvent, QRegion, QPainter, QPaintEvent, QColor

from . import FloatingButton


class FloatingCircleButton(FloatingButton):
    def __init__(self, parent, radius, alignment, color: QColor,
                 m_left=0, m_top=0, m_right=0, m_bottom=0):
        super().__init__(alignment, parent=parent)

        self.radius = radius
        self.color = color

        size = QSize(self.radius * 2, self.radius * 2)
        size += QSize(m_left + m_right, m_top + m_bottom)
        self.resize(size)

        self.setContentsMargins(m_left, m_top, m_right, m_bottom)

    def paintEvent(self, event: QPaintEvent):
        self._draw_circle()

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

        # Circle mask
        self.setMask(QRegion(button_rect, QRegion.Ellipse))

        super().resizeEvent(event)

    def _draw_circle(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = Qt.NoPen
        painter.setPen(pen)

        palette = self.palette()
        # I have no clue why isDown needs to be flipped here
        brush = self.color if not self.isDown() else palette.shadow()
        painter.setBrush(brush)

        m_left, m_top, _, _ = self.getContentsMargins()
        painter.drawEllipse(QPoint(self.radius + m_left, self.radius + m_top),
                            self.radius, self.radius)
