from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsRectItem


class AlertBanner(QGraphicsRectItem):

    def __init__(self, width, height, color=Qt.darkGray, parent=None):
        super().__init__(0, 0, width, height, parent=parent)

        pen = self.pen()
        brush = self.brush()

        self.color = QColor(color)



