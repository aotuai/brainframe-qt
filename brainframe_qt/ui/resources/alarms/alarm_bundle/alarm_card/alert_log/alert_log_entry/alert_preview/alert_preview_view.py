from PyQt5.QtCore import QRectF, Qt, QRect
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QWidget


class AlertPreviewView(QGraphicsView):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setScene(QGraphicsScene())

    def hasHeightForWidth(self):
        """Enable the use of heightForWidth"""
        return True

    def heightForWidth(self, width: int):

        if self.scene().width() == 0:
            return 0

        aspect_ratio = self.scene().height() / self.scene().width()
        height = width * aspect_ratio

        return height

    # # Python reimplementation of original Qt source without the 2px margin
    # # https://bugreports.qt.io/browse/QTBUG-42331 - based on QT sources
    # def fitInView(self, rect, flags=Qt.IgnoreAspectRatio):
    #     if self.scene() is None or rect.isNull():
    #         return
    #
    #     # Reset the view scale to 1:1
    #     unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
    #     if unity.isEmpty():
    #         return
    #     self.scale(1 / unity.width(), 1 / unity.height())
    #
    #     # Find the ideal x/y scaling ration to fit rect in the view
    #     view_rect = self.viewport().rect()
    #     if view_rect.isEmpty():
    #         return
    #     scene_rect = self.transform().mapRect(rect)
    #     if scene_rect.isEmpty():
    #         return
    #     x_ratio = view_rect.width() / scene_rect.width()
    #     y_ratio = view_rect.height() / scene_rect.height()
    #
    #     # Respect the aspect ratio
    #     if flags == Qt.KeepAspectRatio:
    #         x_ratio = y_ratio = min(x_ratio, y_ratio)
    #     elif flags == Qt.KeepAspectRatioByExpanding:
    #         x_ratio = y_ratio = max(x_ratio, y_ratio)
    #
    #     # Scale and center on the center of rect
    #     self.scale(x_ratio, y_ratio)
    #     self.centerOn(rect.center())

    # Slightly better than the above implementation due to having 1 fewer
    # scale -> width (as int) -> scale
    # This effects the right side of the image not aligned properly to its
    # view. Still not perfect, though.
    # https://bugreports.qt.io/browse/QTBUG-42331
    def fitInView(self, rect: QRectF, flags=Qt.IgnoreAspectRatio):

        if self.scene() is None or rect.isNull():
            return

        view_rect: QRect = self.viewport().rect()
        if view_rect.isEmpty():
            return
        scene_rect: QRect = self.transform().mapRect(rect)
        if scene_rect.isEmpty():
            return

        view_width = view_rect.width()
        view_height = view_rect.height()

        scene_width = scene_rect.width()
        scene_height = scene_rect.height()

        if flags == Qt.KeepAspectRatio:

            if view_width / view_height > scene_width / scene_height:
                # Target wider than source. Will be limited by height
                new_height = view_height
                new_width = (view_height / scene_height) * scene_width
            else:
                # Target taller than source. Will be limited by width
                new_width = view_width
                new_height = (view_width / scene_width) * scene_height

        elif flags == Qt.KeepAspectRatioByExpanding:

            if view_width / view_height > scene_width / scene_height:
                # Target wider than source. Will be limited by width
                new_width = view_width
                new_height = (view_width / scene_width) * scene_height
            else:
                # Target taller than source. Will be limited by height
                new_height = view_height
                new_width = (view_height / scene_height) * scene_width

        else:  # flags == Qt.IgnoreAspectRatio:

            new_width = view_width
            new_height = view_height

        scale_width = new_width / scene_width
        scale_height = new_height / scene_height

        self.scale(scale_width, scale_height)
