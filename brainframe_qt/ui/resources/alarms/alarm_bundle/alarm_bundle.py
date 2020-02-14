from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.paths import qt_qss_paths
from brainframe.client.ui.resources.alarms.alarm_bundle.alarm_card \
    import AlarmCard


class AlarmBundleUI(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QVBoxLayout()
        self.setLayout(layout)

    def _init_style(self):
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alarm_bundle_qss)


class AlarmBundle(AlarmBundleUI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        for _ in range(3):
            self.add_alarm_card()

    def add_alarm_card(self):
        self.layout().addWidget(AlarmCard(self))


if __name__ == '__main__':
    import typing
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    app.setAttribute(Qt.AA_EnableHighDpiScaling)

    window = QWidget()
    window.setAttribute(Qt.WA_StyledBackground, True)

    window.setLayout(QVBoxLayout(window))
    window.layout().addWidget(AlarmBundle(typing.cast(QWidget, None)))

    window.show()

    app.exec_()
