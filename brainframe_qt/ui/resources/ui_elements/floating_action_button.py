import math

from PyQt5.QtCore import Qt, QEvent, QObject, QPoint
from PyQt5.QtGui import QBrush, QLinearGradient, QPainter, QPaintEvent
from PyQt5.QtWidgets import QAbstractButton


class FloatingActionButton(QAbstractButton):
    def __init__(self, radius, corner_offset, parent=None):
        super().__init__(parent=parent)

        self.radius = radius
        self.resize(self.radius * 2, self.radius * 2)
        self.size_offset = QPoint(self.radius * 2, self.radius * 2)
        self.corner_offset = QPoint(corner_offset, corner_offset)

        if self.parent():
            self.parent().installEventFilter(self)

    def eventFilter(self, obj: QObject, event: QEvent):
        if obj is self.parent():
            if event.type() in [QEvent.Resize, QEvent.Move]:
                self.update_location()
        return False

    def hitButton(self, pos: QPoint) -> bool:
        center_x, center_y = self.radius, self.radius
        mouse_x, mouse_y = pos.x(), pos.y()

        distance = math.hypot(center_x - mouse_x, center_y - mouse_y)
        return distance <= self.radius

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
        painter.drawEllipse(QPoint(self.radius, self.radius),
                            self.radius, self.radius)

    def _draw_plus(self, painter: QPainter):
        palette = self.palette()
        brush = palette.window()
        painter.setBrush(brush)

        rect_width = self.radius / 5
        rect_length = self.radius

        center_x, center_y = self.radius, self.radius

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

    def update_location(self):

        parent_size = self.parent().size()
        parent_bottom_right = QPoint(parent_size.width(), parent_size.height())

        location = parent_bottom_right - self.size_offset - self.corner_offset
        self.move(location)
