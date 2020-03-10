from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QLayout, QSizePolicy

from brainframe.client.api.codecs import ZoneAlarm
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
        # Start with 0 spacing between BundleHeader and (empty) alarm_container
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(self.bundle_header)
        layout.addWidget(self.alarm_container)

        self.setLayout(layout)

    def _init_style(self):
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        # Use a fixed amount of vertical space
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        stylesheet_watcher.watch(self, qt_qss_paths.alarm_bundle_qss)

    def _init_alarm_container(self) -> QWidget:
        alarm_container = QFrame(self)
        alarm_container.setObjectName("alarm_container")

        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setAlignment(Qt.AlignTop)

        alarm_container.setLayout(container_layout)

        return alarm_container

    def _init_bundle_header(self) -> QWidget:
        bundle_header = BundleHeader(self)
        return bundle_header


class AlarmBundle(AlarmBundleUI, ExpandableMI, IterableMI):

    def __init__(self, bundle_name: str,
                 parent: QWidget):
        super().__init__(parent)

        self._init_signals()

        self.bundle_name = bundle_name
        self.bundle_header.set_bundle_name(bundle_name)

    def __contains__(self, alarm):
        if isinstance(alarm, AlarmCard):
            return alarm in self.__iter__()

        elif isinstance(alarm, ZoneAlarm):
            try:
                self[alarm]
            except KeyError:
                return False
            return True

        else:
            return super().__contains__(alarm)

    def __getitem__(self, alarm: ZoneAlarm) -> AlarmCard:
        if isinstance(alarm, ZoneAlarm):
            search = (alarm_card for alarm_card in self
                      if alarm_card.alarm.id == alarm.id)
            try:
                return next(search)
            except StopIteration as exc:
                raise KeyError from exc
        else:
            raise TypeError

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
        if self.iterable_layout().count() == 0:
            self.layout().setSpacing(0)
        else:
            self.layout().setSpacing(-1)

        stylesheet_watcher.update_widget(self)

    def iterable_layout(self) -> QLayout:
        return self.alarm_container.layout()

    def add_alarm_card(self, alarm: ZoneAlarm):
        alarm_card = AlarmCard(alarm, self)
        self.alarm_container.layout().addWidget(alarm_card)

        # Add spacing back between BundleHeader and alarm_container
        if self.layout().spacing() == 0:
            self.layout().setSpacing(-1)

    def del_alarm_card(self, alarm: ZoneAlarm):
        alarm_card = self[alarm]
        self.alarm_container.layout().removeWidget(alarm_card)

        # Remove between BundleHeader and (empty) alarm_container
        if self.iterable_layout().count() == 0:
            self.layout().setSpacing(0)


if __name__ == '__main__':
    import typing
    from PyQt5.QtWidgets import QApplication

    # noinspection PyArgumentList
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication([])

    # noinspection PyArgumentList
    window = QWidget()
    window.setAttribute(Qt.WA_StyledBackground, True)

    window.setLayout(QVBoxLayout())
    window.layout().addWidget(AlarmBundle("Bundle name",
                                          typing.cast(QWidget, None)))

    window.show()

    app.exec_()
