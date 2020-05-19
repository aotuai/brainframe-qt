import typing
from typing import Optional

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QWidget

from brainframe.client.api_utils import api
from brainframe.api.bf_codecs import Alert
# noinspection PyUnresolvedReferences
from brainframe.client.ui.resources import QTAsyncWorker, qt_resources, \
    stylesheet_watcher
from brainframe.client.ui.resources.alarms.alarm_bundle.alarm_card.alert_log \
    .alert_log_entry.alert_preview.alert_detail import AlertDetail
from brainframe.client.ui.resources.paths import qt_qss_paths
from brainframe.client.ui.resources.ui_elements.widgets import ImageLabel


class AlertPreviewUI(QFrame):
    _loading_image = typing.cast(QPixmap, None)
    _no_image_available_image = typing.cast(QPixmap, None)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.image_label = self._init_image_label()
        self.alert_detail = self._init_alert_detail()

        self._init_layout()
        self._init_style()

    def _init_image_label(self) -> ImageLabel:
        image_label = ImageLabel(self)
        return image_label

    def _init_alert_detail(self) -> AlertDetail:
        alert_detail = AlertDetail(self)
        return alert_detail

    def _init_layout(self) -> None:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(0)

        layout.addWidget(self.image_label)
        layout.addWidget(self.alert_detail)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alert_preview_qss)

    def setVisible(self, visible: bool) -> None:
        super().setVisible(visible)

        # Workaround. No idea how to do this gracefully
        parent = self.parentWidget()
        while parent:
            parent.updateGeometry()
            parent = parent.parentWidget()

    @classmethod
    def _get_loading_image(cls):
        """Cache the loading SVG as a 1920x1080 pixmap"""
        if cls._loading_image is None:
            icon = QIcon(":/images/loading_image_svg")
            cls._loading_image = icon.pixmap(1920, 1080)
        return cls._loading_image

    @classmethod
    def _get_no_image_available_image(cls):
        """Cache the no image available SVG as a 1920x1080 pixmap"""
        if cls._no_image_available_image is None:
            icon = QIcon(":/images/no_image")
            cls._no_image_available_image = icon.pixmap(1920, 1080)
        return cls._no_image_available_image


class AlertPreview(AlertPreviewUI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.alert = typing.cast(Alert, None)

    def populate_from_server(self):

        if not self.alert:
            return

        self.load_alert_image()
        self.alert_detail.populate_from_server()

    def load_alert_image(self):

        def handle_frame(frame: Optional[np.ndarray]):

            if frame is None:
                self.image_label.pixmap_ = self._get_no_image_available_image()
            else:
                self.image_label.set_ndarray(frame)

        self.image_label.pixmap_ = self._get_loading_image()

        QTAsyncWorker(self, api.get_alert_frame, f_args=(self.alert.id,),
                      on_success=handle_frame) \
            .start()

    def set_alert(self, alert):
        self.alert = alert
        self.alert_detail.set_alert(alert)


if __name__ == '__main__':
    import typing
    from PyQt5.QtWidgets import QApplication, QDesktopWidget, QVBoxLayout

    api.set_url("http://localhost")

    # noinspection PyArgumentList
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication([])

    # noinspection PyArgumentList
    window = QWidget()
    window.setWindowFlags(Qt.WindowStaysOnTopHint)
    window.resize(QDesktopWidget().availableGeometry(window).size() * .4)
    window.setAttribute(Qt.WA_StyledBackground, True)

    window.setLayout(QVBoxLayout())
    widget = AlertPreview(typing.cast(QWidget, None))
    window.layout().addWidget(widget)

    window.show()

    app.exec_()
