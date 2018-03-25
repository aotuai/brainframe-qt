from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QSizePolicy

from visionapp.client.ui.resources.paths import image_paths


class NewStreamButton(QLabel):

    new_stream_button_clicked = pyqtSignal()
    """Signaled when expanded stream is closed"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.pixmap = QPixmap(str(image_paths.new_stream_icon))

        # Also sets the pixmap
        self._fix_pixmap_size()

    def resizeEvent(self, event):
        self._fix_pixmap_size()
        super().resizeEvent(event)

    def mouseReleaseEvent(self, event):
        self.new_stream_button_clicked.emit()
        super().mouseReleaseEvent(event)

    def _fix_pixmap_size(self):
        """Adjust the pixmap to be sized to fit in the label"""
        widget_width = self.width()
        widget_height = self.height()
        self.setPixmap(self.pixmap.scaled(widget_width,
                                          widget_height,
                                          Qt.KeepAspectRatio))


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = NewStreamButton()
    window.show()

    app.exec_()