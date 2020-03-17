import logging
from typing import Optional

import numpy as np

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QGraphicsPixmapItem

from brainframe.client.api import api
from brainframe.client.api.codecs import Alert
from brainframe.client.ui.resources import stylesheet_watcher, QTAsyncWorker
from brainframe.client.ui.resources.paths import qt_qss_paths

from .alert_preview_view import AlertPreviewView
from .alert_detail import AlertDetail


class AlertPreviewUI(QFrame):
    def __init__(self, alert: Alert, parent: QWidget):
        super().__init__(parent)

        self.alert = alert

        self.image_item = self._init_image_item()
        self.alert_image_view = self._init_alert_image_view()
        self.alert_detail = self._init_alert_detail()

        self._init_layout()
        self._init_style()

    def resizeEvent(self, event=None):
        """Take up entire width using aspect ratio of scene"""

        bounding_rect = self.image_item.boundingRect()
        self.alert_image_view.scene().setSceneRect(bounding_rect)
        self.alert_image_view.fitInView(bounding_rect, Qt.KeepAspectRatio)

    def _init_image_item(self) -> QGraphicsPixmapItem:
        image_item = QGraphicsPixmapItem(QPixmap())

        return image_item

    def _init_alert_image_view(self) -> AlertPreviewView:
        alert_image_view = AlertPreviewView(self)
        alert_image_view.scene().addItem(self.image_item)

        return alert_image_view

    def _init_alert_detail(self) -> AlertDetail:
        return AlertDetail(self)

    def _init_layout(self) -> None:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.alert_image_view)
        layout.addWidget(self.alert_detail)

        layout.setStretch(0, 2)
        layout.setStretch(1, 3)

        self.setLayout(layout)

    def _init_style(self) -> None:

        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alert_preview_qss)


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

            image = self._ndarray_to_qimage(frame)
            self.set_image(image)

        QTAsyncWorker(self, api.get_alert_frame, f_args=(self.alert.id,),
                      on_success=handle_frame) \
            .start()

    def set_image(self, image: QImage):
        self.image_item.setPixmap(QPixmap(image))
        self.alert_image_view.fitInView(self.image_item.boundingRect(),
                                        Qt.KeepAspectRatio)

    @staticmethod
    def _ndarray_to_qimage(array: np.ndarray) -> QImage:
        height, width, channels = array.shape
        bytesPerLine = channels * width
        image = QImage(array.data, width, height, bytesPerLine,
                       QImage.Format_RGB888).rgbSwapped()

        return image
