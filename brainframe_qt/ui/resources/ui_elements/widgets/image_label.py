import numpy as np
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QResizeEvent
from PyQt5.QtWidgets import QLabel, QWidget

from brainframe.client.ui.resources.paths import image_paths


class _ImageLabelUI(QLabel):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._image = QImage(str(image_paths.error))
        self._update_pixmap()

        # Without this set, the image will grow but not shrink
        self.setMinimumSize(1, 1)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        if self._image is None:
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
    def image(self) -> QImage:
        return self._image

    @image.setter
    def image(self, image: QImage):
        self._image = image
        self._update_pixmap()

    def _update_pixmap(self):
        pixmap = QPixmap(self.image)

        if self.hasHeightForWidth():
            # Use width to decide initial height
            image_size = self.image.size().scaled(self.width(), 999999999,
                                                  Qt.KeepAspectRatio)
        else:
            image_size = self.image.size().scaled(self.size(),
                                                  Qt.KeepAspectRatio)

        # Ensure larger than minimum size
        min_size = image_size.expandedTo(self.minimumSize())
        image_size = image_size.scaled(min_size, Qt.KeepAspectRatioByExpanding)

        # Ensure smaller than maximum size
        max_size = image_size.boundedTo(self.maximumSize())
        image_size = image_size.scaled(max_size, Qt.KeepAspectRatio)

        # Scale the image
        scaled_pixmap = pixmap.scaled(image_size,
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

        self.image = image
