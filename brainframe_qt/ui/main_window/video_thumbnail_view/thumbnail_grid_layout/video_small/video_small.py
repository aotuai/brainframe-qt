from PyQt5.QtCore import pyqtSignal, QRectF, Qt
from PyQt5.QtGui import QPainter, QColor, QImage

from brainframe.client.ui.resources.paths import image_paths
from brainframe.client.ui.resources.video_items.stream_widget import (
    StreamWidget, DetectionPolygon, ZoneStatusPolygon
)


class VideoSmall(StreamWidget):
    """Video for ThumbnailView"""

    stream_clicked = pyqtSignal(object)
    """Alerts the layout view that a thumbnail has been clicked
    
    Connected to:
    - ThumbnailGridLayout -- Dynamic
      [parent].thumbnail_stream_clicked_slot
    """
    ongoing_alerts_signal = pyqtSignal(bool)
    """Alerts the layout view that the stream has a change in the state of its
    ongoing alert
    
    Connected to:
    - ThumbnailGridLayout -- Dynamic
      [parent].ongoing_alerts_slot
    """

    def __init__(self, parent=None, stream_conf=None, frame_rate=30):
        super().__init__(stream_conf, frame_rate, parent=parent)

        self.ongoing_alerts: bool = False

    def update_items(self):
        """Override the base StreamWidget implementation to add alert UI
        functionality

        # TODO: Is this _really_ the best way of doing this?
        """

        frame = self.video_stream.latest_processed_frame_rgb

        # Only update detections & zones when needed
        if self.stream_is_up and frame is not None:
            if frame.tstamp != self.timestamp:
                self.update_latest_zones(frame.zone_statuses)
                self.update_latest_detections(frame.zone_statuses)

                self.manage_alert_indication(frame.zone_statuses)

        else:
            self.remove_items_by_type(DetectionPolygon)
            self.remove_items_by_type(ZoneStatusPolygon)

        self.update_frame()

    def manage_alert_indication(self, zone_statuses):

        # Get all alerts in each zone_status as a single list
        # [Unused]. Might be helpful in future when we need to know more info
        # alerts = [alert for zone_status in zone_statuses
        #           for alert in zone_status.alerts]

        # Any active alerts?
        alerts = any(zone_status.alerts for zone_status in zone_statuses)

        # self.ongoing_alerts is used during every paint in drawForeground
        if alerts and not self.ongoing_alerts:
            self.ongoing_alerts = True
            # noinspection PyUnresolvedReferences
            self.ongoing_alerts_signal.emit(True)
        elif not alerts and self.ongoing_alerts:
            self.ongoing_alerts = False
            # noinspection PyUnresolvedReferences
            self.ongoing_alerts_signal.emit(False)

    def drawForeground(self, painter: QPainter, rect: QRectF):
        """Draw the alert UI if there are ongoing alerts

        Alert is at the bottom of the QGraphics view, full width and 1/3 height.
        Text is positioned manually such that it looks nice within alert.
        Icon is positioned manually such that it looks nice within alert.

        Overrides the super().drawForeground method which by default does pretty
        much nothing
        """
        if self.ongoing_alerts:
            # Gray rectangle
            brush = painter.brush()
            brush.setColor(QColor(0, 0, 0, 127))  # Half transparent black
            brush.setStyle(Qt.SolidPattern)
            painter.setBrush(brush)

            # No border
            painter.setPen(Qt.NoPen)

            # Draw alert background
            painter.fillRect(0,
                             int(self.sceneRect().height() * 2 / 3),
                             int(self.sceneRect().width()),
                             int(self.sceneRect().height() / 3),
                             painter.brush())

            # Draw text
            font = painter.font()
            point_size = int(self.sceneRect().height() / 6)
            font.setPointSize(point_size if point_size > 0 else 1)
            painter.setFont(font)
            painter.setPen(Qt.white)

            painter.drawText(int(self.sceneRect().width() / 24),
                             int(self.sceneRect().height() * 11 / 12), "Alert!")

            # Draw icon
            image = QImage(str(image_paths.alert_icon))
            image = image.scaled(int(self.sceneRect().width()),
                                 int(self.sceneRect().height() / 6),
                                 Qt.KeepAspectRatio)
            painter.drawImage(
                int(self.sceneRect().width() * 23 / 24) - image.width(),
                int(self.sceneRect().height() * 11 / 12) - image.height(),
                image)

    def mouseReleaseEvent(self, event):
        # Add border around stream to indicate its selection
        self.add_selection_border()

        # noinspection PyUnresolvedReferences
        self.stream_clicked.emit(self.stream_conf)

        super().mousePressEvent(event)

    def add_selection_border(self):
        """Add border around stream"""
        pass

    def remove_selection_border(self):
        """Remove border around stream"""
        pass
