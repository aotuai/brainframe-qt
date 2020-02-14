from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame

from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.alarms.alarm_bundle.bundle_header import \
    BundleHeader
from brainframe.client.ui.resources.paths import qt_qss_paths
from brainframe.client.ui.resources.alarms.alarm_bundle.alarm_card \
    import AlarmCard


class AlarmBundleUI(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.bundle_header = self._init_bundle_header()
        self.alarm_container = self._init_alarm_container()

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.bundle_header)
        layout.addWidget(self.alarm_container)

        self.setLayout(layout)

    def _init_style(self):
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alarm_bundle_qss)

    def _init_alarm_container(self) -> QWidget:
        alarm_container = QFrame(self)
        alarm_container.setObjectName("alarm_container")
        alarm_container.setLayout(QVBoxLayout())
        return alarm_container

    def _init_bundle_header(self) -> QWidget:
        bundle_header = BundleHeader(self)
        return bundle_header


class AlarmBundle(AlarmBundleUI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        for _ in range(3):
            self.add_alarm_card()

    def add_alarm_card(self):
        self.alarm_container.layout().addWidget(AlarmCard(self))


if __name__ == '__main__':
    import typing
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    app.setAttribute(Qt.AA_EnableHighDpiScaling)

    window = QWidget()
    window.setAttribute(Qt.WA_StyledBackground, True)

    window.setLayout(QVBoxLayout())
    window.layout().addWidget(AlarmBundle(typing.cast(QWidget, None)))

    window.show()

    app.exec_()
