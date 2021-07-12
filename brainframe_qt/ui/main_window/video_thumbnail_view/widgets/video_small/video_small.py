from PyQt5.QtCore import QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFontMetricsF, QImage, QPainter, QMouseEvent
from PyQt5.QtWidgets import QWidget
from brainframe.api.bf_codecs import StreamConfiguration

from brainframe_qt.api_utils import get_stream_manager
from brainframe_qt.ui.resources.video_items.streams import StreamWidget


class VideoSmall(StreamWidget):
    """Video for ThumbnailView"""

    stream_clicked = pyqtSignal(StreamConfiguration)
    """A thumbnail has been clicked"""

    alert_status_changed = pyqtSignal(bool)
    """The stream's ongoing alert state has changed"""

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)

        self.alerts_ongoing: bool = False

    def drawForeground(self, painter: QPainter, rect: QRectF):
        """Draw the alert UI if there are ongoing alerts

        Alert is at the bottom of the QGraphics view, full width and 1/3 height.
        Text is positioned manually such that it looks nice within alert.
        Icon is positioned manually such that it looks nice within alert.

        Overrides the super().drawForeground method which by default does pretty much
        nothing
        """
        # Gray rectangle
        brush = painter.brush()
        brush.setColor(QColor(0, 0, 0, 127))  # Half transparent black
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)

        # No border
        painter.setPen(Qt.NoPen)

        width = self.scene().width()
        height = self.scene().height()
        bar_percent = .1

        bar_height = width * bar_percent

        # Draw alert background
        painter.fillRect(0, int(height - bar_height),
                         int(width), int(bar_height),
                         painter.brush())

        image_width_with_margins = 0
        if self.alerts_ongoing:
            # Draw icon
            image_percent = 0.8

            image = QImage(":/icons/alert")
            image = image.scaled(int(self.sceneRect().width()),
                                 int(bar_height * image_percent),
                                 Qt.KeepAspectRatio)

            image_margin = bar_height / 4
            painter.drawImage(
                int(width - image.width() - image_margin),
                int(height - image.height()
                    - (bar_height * (1 - image_percent) / 2)),
                image)

            image_width_with_margins = image.width() + (2.5 * image_margin)

        if self.stream_event_manager.stream_conf is not None:
            # Draw text
            font = painter.font()
            point_size = bar_height / 2
            font.setPointSizeF(point_size if point_size > 0 else 1)
            painter.setFont(font)
            painter.setPen(Qt.white)

            font_metric = QFontMetricsF(font)
            stream_name_text = font_metric.elidedText(
                self.stream_event_manager.stream_conf.name,
                Qt.ElideRight,
                width - image_width_with_margins)

            painter.drawText(int(point_size / 2),
                             int(height - (point_size / 2)),
                             stream_name_text)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)

        if event.button() == Qt.LeftButton:
            self.stream_clicked.emit(self.stream_event_manager.stream_conf)

    def manage_alert_state(self, alerts_active: bool) -> None:
        self.alerts_ongoing = alerts_active
