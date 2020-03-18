import logging
from typing import Optional

import numpy as np

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QResizeEvent
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QLabel

from brainframe.client.api import api
from brainframe.client.api.codecs import Alert
from brainframe.client.ui.resources import stylesheet_watcher, QTAsyncWorker
from brainframe.client.ui.resources.paths import qt_qss_paths

from .alert_detail import AlertDetail


class AlertPreviewUI(QFrame):
    def __init__(self, alert: Alert, parent: QWidget):
        super().__init__(parent)

        self.alert = alert
        self._image = QImage()

        self.image_label = self._init_image_label()
        self.alert_detail = self._init_alert_detail()

        self._init_layout()
        self._init_style()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self._set_image()

    def _init_image_label(self) -> QLabel:
        image_label = QLabel(self)

        return image_label

    def _init_alert_detail(self) -> AlertDetail:
        alert_detail = AlertDetail(self)
        return alert_detail

    def _init_layout(self) -> None:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.image_label)
        layout.addWidget(self.alert_detail)

        layout.setStretch(0, 2)
        layout.setStretch(1, 3)

        self.setLayout(layout)

    def _init_style(self) -> None:

        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alert_preview_qss)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image: QImage):
        self._image = image

    def _set_image(self):
        pixmap = QPixmap(self.image)
        pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatioByExpanding)
        self.image_label.setPixmap(pixmap)

    def setVisible(self, visible: bool) -> None:
        super().setVisible(visible)

        # Workaround. No idea how to do this gracefully
        parent = self.parentWidget()
        while parent:
            parent.updateGeometry()
            parent = parent.parentWidget()


class AlertPreview(AlertPreviewUI):

    def __init__(self, alert: Alert, parent: QWidget):
        super().__init__(alert, parent)

        self.load_alert_image()
        self.alert_detail.set_alert(alert)

    def load_alert_image(self):

        def handle_frame(frame: Optional[np.ndarray]):
            if frame is None:
                # TODO: Handle a missing frame
                logging.warning("TODO: No frame for alert found")
                return

            self.image = self._ndarray_to_qimage(frame)

        QTAsyncWorker(self, api.get_alert_frame, f_args=(self.alert.id,),
                      on_success=handle_frame) \
            .start()

    @staticmethod
    def _ndarray_to_qimage(array: np.ndarray) -> QImage:
        height, width, channels = array.shape
        bytesPerLine = channels * width
        image = QImage(array.data, width, height, bytesPerLine,
                       QImage.Format_RGB888).rgbSwapped()

        return image
