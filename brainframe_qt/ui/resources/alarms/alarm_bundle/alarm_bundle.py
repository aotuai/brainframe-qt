import enum
import functools
from enum import Enum
from typing import List, Union

from PyQt5.QtCore import Qt, pyqtSlot, QThread, QMetaObject, Q_ARG
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, \
    QLayout, QSizePolicy, QApplication

from brainframe.api.codecs import StreamConfiguration, ZoneAlarm, Zone
from brainframe.client.api_utils.zss_pubsub import zss_publisher
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

    def _init_bundle_header(self) -> BundleHeader:
        bundle_header = BundleHeader(self)
        return bundle_header


class AlarmBundle(AlarmBundleUI, ExpandableMI, IterableMI):

    class BundleType(Enum):
        BY_STREAM = enum.auto()
        BY_ZONE = enum.auto()

    def __init__(self, bundle_mode: BundleType,
                 bundle_codec: Union[StreamConfiguration, Zone],
                 parent: QWidget):
        super().__init__(parent)

        # noinspection PyTypeHints
        self.bundle_mode: self.BundleType = bundle_mode
        self.bundle_codec: Union[StreamConfiguration, Zone] = bundle_codec

        self._populate_bundle_header()

        self._init_signals()

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

        subscribe_alarms = functools.partial(zss_publisher.subscribe_alarms,
                                             self.handle_alarm_stream)

        if self.bundle_mode is AlarmBundle.BundleType.BY_STREAM:
            subscription = subscribe_alarms(stream_id=self.bundle_codec.id)
        elif self.bundle_mode is AlarmBundle.BundleType.BY_ZONE:
            subscription = subscribe_alarms(zone_id=self.bundle_codec.id)
        else:
            return

        self.destroyed.connect(lambda: zss_publisher.unsubscribe(subscription))

    def _populate_bundle_header(self) -> None:
        self.bundle_header.bundle_name = self.bundle_codec.name

        if self.bundle_mode is AlarmBundle.BundleType.BY_STREAM:
            bundle_location = QApplication.translate("AlarmBundle", "(Stream)")
        elif self.bundle_mode is AlarmBundle.BundleType.BY_ZONE:
            # TODO: Translate
            bundle_location = "in Zone '{}'".format(self.bundle_codec.name)
        else:
            return

        self.bundle_header.bundle_location = bundle_location

    def expand(self, expanding: bool):

        # Collapse all AlarmCards before collapsing the bundle
        if not expanding:
            for alarm_card in self:
                alarm_card: AlarmCard
                alarm_card.expanded = False

        self.alarm_container.setVisible(expanding)
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

    @pyqtSlot(object)
    def handle_alarm_stream(self, server_alarms: List[ZoneAlarm]):
        """Add new alarms when the ZSS gets them"""

        if QThread.currentThread() != self.thread():
            # Move to the UI Thread
            QMetaObject.invokeMethod(self, self.handle_alarm_stream.__name__,
                                     Qt.QueuedConnection,
                                     Q_ARG("PyQt_PyObject", server_alarms))
            return

        server_alarms = {alarm.id: alarm for alarm in server_alarms}
        local_alarms = {alarm_card.alarm.id: alarm_card.alarm
                        for alarm_card in self}

        new_alarm_ids = set(server_alarms).difference(local_alarms)
        del_alarm_ids = set(local_alarms).difference(server_alarms)

        new_alarms = {alarm_id: server_alarms[alarm_id]
                      for alarm_id in new_alarm_ids}
        del_alarms = {alarm_id: local_alarms[alarm_id]
                      for alarm_id in del_alarm_ids}

        for new_alarm in new_alarms.values():
            self.add_alarm_card(new_alarm)

        for del_alarm in del_alarms.values():
            self.del_alarm_card(del_alarm)


if __name__ == '__main__':
    import typing

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
