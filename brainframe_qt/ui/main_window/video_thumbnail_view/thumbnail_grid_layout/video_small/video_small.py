from PyQt5.QtCore import QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFontMetricsF, QImage, QPainter
from PyQt5.QtWidgets import QWidget

from brainframe_qt.api_utils.streaming.zone_status_frame import ZoneStatusFrame
from brainframe_qt.ui.resources.video_items.streams import StreamWidget


class VideoSmall(StreamWidget):
    """Video for ThumbnailView"""

    stream_clicked = pyqtSignal(object)
    """A thumbnail has been clicked"""

    ongoing_alerts_signal = pyqtSignal(bool)
    """The stream's ongoing alert state has changed"""

    def __init__(self, parent: QWidget):

        self.alerts_ongoing: bool = False

        super().__init__(parent=parent)

    def on_frame(self, frame: ZoneStatusFrame):
        super().on_frame(frame)

        # zone_statuses can be None if the server has never once returned a
        # result for this stream.
        if frame.zone_statuses is not None:
            self.manage_alert_indication(frame.zone_statuses)

    def manage_alert_indication(self, zone_statuses):

        # Any active alerts?
        alerts = any(zone_status.alerts for zone_status in zone_statuses.values())

        # self.ongoing_alerts is used during every paint in drawForeground
        if alerts and not self.alerts_ongoing:
            self.alerts_ongoing = True
            self.ongoing_alerts_signal.emit(True)
        elif not alerts and self.alerts_ongoing:
            self.alerts_ongoing = False
            self.ongoing_alerts_signal.emit(False)

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

        # Draw text
        font = painter.font()
        point_size = bar_height / 2
        font.setPointSizeF(point_size if point_size > 0 else 1)
        painter.setFont(font)
        painter.setPen(Qt.white)

        font_metric = QFontMetricsF(font)
        stream_name_text = font_metric.elidedText(
            self.stream_manager.stream_conf.name,
            Qt.ElideRight,
            width - image_width_with_margins)

        painter.drawText(int(point_size / 2),
                         int(height - (point_size / 2)),
                         stream_name_text)

    def mouseReleaseEvent(self, event):
        super().mousePressEvent(event)

        self.stream_clicked.emit(self.stream_manager.stream_conf)
