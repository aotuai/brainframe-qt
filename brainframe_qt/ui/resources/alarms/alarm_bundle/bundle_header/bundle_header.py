from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.paths import qt_qss_paths


class BundleHeaderUI(QFrame):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.bundle_name_label = self._init_bundle_name_label()

        self._init_layout()
        self._init_style()

    def _init_bundle_name_label(self) -> QLabel:
        bundle_name_layout = QLabel("Stream 1", self)
        return bundle_name_layout

    def _init_layout(self) -> None:
        layout = QHBoxLayout()

        layout.addWidget(self.bundle_name_label)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.bundle_header_qss)


class BundleHeader(BundleHeaderUI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)
