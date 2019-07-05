from abc import ABC, abstractmethod

from PyQt5.QtCore import Qt, QEvent, QObject, QPoint, QRect
from PyQt5.QtGui import QPaintEvent, QMouseEvent, QRegion
from PyQt5.QtWidgets import QAbstractButton


class FloatingButton(QAbstractButton):

    def __init__(self, alignment: Qt.AlignmentFlag, parent):
        super().__init__(parent=parent)

        self.alignment: Qt.AlignmentFlag = alignment

        self.parent().installEventFilter(self)
        self.update_location()

    def eventFilter(self, obj: QObject, event: QEvent):
        if obj is self.parent():
            if event.type() in [QEvent.Resize, QEvent.Move]:
                self.update_location()
        return False

    def update_location(self):

        m_left, m_top, m_right, m_bottom = self.parent().getContentsMargins()

        # X
        if self.alignment & Qt.AlignLeft:
            x = self.parent().rect().left() + m_left
        elif self.alignment & Qt.AlignHCenter:
            x = self.parent().rect().center().x() - (self.width() / 2)
        elif self.alignment & Qt.AlignRight:
            x = self.parent().width() - self.width() - m_right
        else:
            raise ValueError("Unknown alignment")

        # Y
        if self.alignment & Qt.AlignTop:
            y = self.parent().rect().top() + m_top
        elif self.alignment & Qt.AlignVCenter:
            y = self.parent().rect().center().y() - (self.height() / 2)
        elif self.alignment & Qt.AlignBottom:
            y = self.parent().height() - self.height() - m_bottom
        else:
            raise ValueError("Unknown alignment")

        self.move(x, y)
