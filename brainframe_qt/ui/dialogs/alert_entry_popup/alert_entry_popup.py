from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QDialog, QLabel
from PyQt5.QtCore import QSize, Qt
from PyQt5.uic import loadUi

from brainframe_qt.ui.resources.paths import qt_ui_paths
from brainframe_qt.api_utils import api


class AlertEntryPopup(QDialog):
    """Popup to display more information about an alert"""
    alert_frame_label: QLabel

    def __init__(self, alert_message, alert_id, parent=None):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.alert_entry_popup_ui, self)

        self.alert_text_label.setText(alert_message)

        self.alert_frame_label.setPixmap(self.get_frame(alert_id))
        # self.alert_frame_label.setScaledContents(True)

        # self.setMaximumSize(1000, 1000)

    @classmethod
    def show_alert(cls, alert_message, alert_id, parent):
        dialog = cls(alert_message, alert_id, parent=parent)
        dialog.exec_()

    def get_frame(self, alert_id):
        frame = api.get_alert_frame(alert_id)

        if frame is None:
            icon = QIcon(":/images/no_image_svg")
            return icon.pixmap(QSize(1000, 1000))

        height, width, channels = frame.shape
        bytes_per_line = width * channels

        q_image = QImage(
            frame.data,
            width, height, bytes_per_line,
            QImage.Format_RGB888
        ).rgbSwapped()

        pixmap = QPixmap(q_image)

        pixmap = pixmap.scaled(QSize(1000, 1000),
                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return pixmap
