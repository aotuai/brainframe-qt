from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy

from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.paths import qt_qss_paths


class AlertDetailUI(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._description = "More than 2 thingamajigs detected in region " \
                            "[Living Room Ceiling] in the past 3 weeks."

        self.alert_description_label = self._init_alert_description_label()

        self._init_layout()
        self._init_style()

    def _init_alert_description_label(self) -> QLabel:
        alert_description_label = QLabel(self._description, self)
        alert_description_label.setObjectName("alert_description")

        alert_description_label.setWordWrap(True)
        alert_description_label.setSizePolicy(QSizePolicy.Preferred,
                                              QSizePolicy.Expanding)
        alert_description_label.setAlignment(Qt.AlignTop)

        return alert_description_label

    def _init_layout(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(self.alert_description_label)

        self.setLayout(layout)

    def _init_style(self) -> None:

        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alert_detail_qss)


class AlertDetail(AlertDetailUI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
