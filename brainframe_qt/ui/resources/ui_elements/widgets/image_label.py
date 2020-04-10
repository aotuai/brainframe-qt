import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QResizeEvent
from PyQt5.QtWidgets import QLabel, QWidget


class _ImageLabelUI(QLabel):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.has_height_for_width = True
        """Must be set before pixmap set"""

        self._pixmap = QPixmap()
        self._update_pixmap()

        # Without this set, the image will grow but not shrink
        self.setMinimumSize(1, 1)

    def hasHeightForWidth(self) -> bool:
        return self.has_height_for_width

    def heightForWidth(self, width: int) -> int:
        if self.pixmap() is None:
            return 0

        return self.pixmap().height()

    def resizeEvent(self, event: QResizeEvent) -> None:

        self._update_pixmap()
        super().resizeEvent(event)

        # Workaround. No idea how to do this gracefully
        parent = self.parentWidget()
        while parent:
            parent.updateGeometry()
            parent = parent.parentWidget()

    @property
    def pixmap_(self) -> QPixmap:
        return self._pixmap

    @pixmap_.setter
    def pixmap_(self, pixmap: QPixmap):
        self._pixmap = pixmap
        self._update_pixmap()

    def _update_pixmap(self):

        # Handle empty pixmap
        if self.pixmap_.isNull():
            # Overwrite existing pixmap with null pixmap if necessary
            if self.pixmap() is not None and not self.pixmap().isNull():
                self.setPixmap(self.pixmap_)
            return

        if self.hasHeightForWidth():
            # Use width to decide initial height
            pixmap_size = self._pixmap.size().scaled(self.width(), 999999999,
                                                     Qt.KeepAspectRatio)
        else:
            pixmap_size = self._pixmap.size().scaled(self.size(),
                                                     Qt.KeepAspectRatio)

        # Ensure larger than minimum size
        min_size = pixmap_size.expandedTo(self.minimumSize())
        pixmap_size = pixmap_size.scaled(min_size,
                                         Qt.KeepAspectRatioByExpanding)

        # Ensure smaller than maximum size
        max_size = pixmap_size.boundedTo(self.maximumSize())
        pixmap_size = pixmap_size.scaled(max_size, Qt.KeepAspectRatio)

        # Scale the image
        scaled_pixmap = self._pixmap.scaled(pixmap_size,
                                            Qt.KeepAspectRatio,
                                            Qt.SmoothTransformation)

        # Apply the image
        self.setPixmap(scaled_pixmap)


class ImageLabel(_ImageLabelUI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

    def set_ndarray(self, array: np.ndarray) -> None:
        height, width, channels = array.shape
        bytes_per_line = channels * width
        image = QImage(array.data, width, height, bytes_per_line,
                       QImage.Format_RGB888).rgbSwapped()

        pixmap = QPixmap(image)

        self.pixmap_ = pixmap
