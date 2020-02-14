from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QLayout

from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.alarms.alarm_bundle.alarm_card \
    import AlarmCard
from brainframe.client.ui.resources.alarms.alarm_bundle.bundle_header import \
    BundleHeader
from brainframe.client.ui.resources.mixins.data_structure import IterableMI
from brainframe.client.ui.resources.mixins.display import ExpandableMI
from brainframe.client.ui.resources.paths import qt_qss_paths


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

        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)

        alarm_container.setLayout(container_layout)

        return alarm_container

    def _init_bundle_header(self) -> QWidget:
        bundle_header = BundleHeader(self)
        return bundle_header


class AlarmBundle(AlarmBundleUI, ExpandableMI, IterableMI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._init_signals()

        for _ in range(3):
            self.add_alarm_card()

    def _init_signals(self):
        self.bundle_header.clicked.connect(self.toggle_expansion)

    def expansion_changed(self):

        # noinspection PyPropertyAccess
        now_expanded = self.expanded

        # Collapse all AlarmCards before collapsing the bundle
        if not now_expanded:
            for alarm_card in self:
                alarm_card: AlarmCard
                alarm_card.expanded = False

        self.alarm_container.setVisible(now_expanded)
        stylesheet_watcher.update()

    def iterable_layout(self) -> QLayout:
        return self.alarm_container.layout()

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
