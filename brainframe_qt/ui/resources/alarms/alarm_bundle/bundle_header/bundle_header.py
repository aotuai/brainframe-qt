from PyQt5.QtCore import Qt, pyqtProperty
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QWidget

from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.mixins.mouse import ClickableMI
from brainframe.client.ui.resources.paths import qt_qss_paths


class BundleHeaderUI(QFrame):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._bundle_name = "[Bundle Name]"
        self._bundle_location = "[Bundle Location]"

        self.bundle_name_label = self._init_bundle_name_label()
        self.bundle_location_label = self._init_bundle_location_label()

        self._init_layout()
        self._init_style()

    def _init_bundle_name_label(self) -> QLabel:
        bundle_name_layout = QLabel(self._bundle_name, self)
        bundle_name_layout.setObjectName("bundle_name")

        bundle_name_layout.setSizePolicy(QSizePolicy.Maximum,
                                         QSizePolicy.Fixed)

        return bundle_name_layout

    def _init_bundle_location_label(self) -> QLabel:
        bundle_location_label = QLabel(self._bundle_location, self)
        bundle_location_label.setObjectName("bundle_location")

        bundle_location_label.setSizePolicy(QSizePolicy.Expanding,
                                            QSizePolicy.Fixed)

        return bundle_location_label

    def _init_layout(self) -> None:
        layout = QHBoxLayout()

        layout.addWidget(self.bundle_name_label)
        layout.addWidget(self.bundle_location_label)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.bundle_header_qss)


class BundleHeader(BundleHeaderUI, ClickableMI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

    @pyqtProperty(str)
    def bundle_name(self) -> str:
        return self._bundle_name

    @bundle_name.setter
    def bundle_name(self, bundle_name: str) -> None:
        self._bundle_name = bundle_name
        self.bundle_name_label.setText(bundle_name)

    @pyqtProperty(str)
    def bundle_location(self) -> str:
        return self._bundle_location

    @bundle_location.setter
    def bundle_location(self, bundle_location: str) -> None:
        self._bundle_location = bundle_location
        self.bundle_location_label.setText(bundle_location)
