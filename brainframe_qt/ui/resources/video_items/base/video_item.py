from typing import Tuple

from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import QGraphicsItem

from brainframe.client.ui.resources.mixins.base_mixin import ABCObject


class VideoItem(QGraphicsItem, metaclass=ABCObject):
    PointType = Tuple[float, float]

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, 0, 0)

    def paint(self, _painter, _option, _widget):
        """No paint"""
        return
