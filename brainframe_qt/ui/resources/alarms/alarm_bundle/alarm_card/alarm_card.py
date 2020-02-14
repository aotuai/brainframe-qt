from typing import Optional

from PyQt5.QtCore import Qt, pyqtProperty
from PyQt5.QtWidgets import QFrame, QSizePolicy, QVBoxLayout, QWidget, QLayout

from brainframe.client.ui.resources import stylesheet_watcher
# TODO: Change to relative imports?
from brainframe.client.ui.resources.alarms.alarm_bundle.alarm_card.alarm_preview \
    import AlarmPreview
from brainframe.client.ui.resources.alarms.alarm_bundle.alarm_card.alert_log \
    import AlertLog
from brainframe.client.ui.resources.mixins.data_structure import IterableMI
from brainframe.client.ui.resources.mixins.display import ExpandableMI
from brainframe.client.ui.resources.paths import qt_qss_paths


class AlarmCardUI(QFrame):

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)

        self.alarm_preview = self._init_alarm_preview()
        self.alert_log = self._init_alert_log()

        self._init_layout()
        self._init_style()

    def _init_layout(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.alarm_preview)
        layout.addWidget(self.alert_log)

        self.setLayout(layout)

    def _init_style(self):
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.alarm_card_qss)

    def _init_alarm_preview(self) -> AlarmPreview:
        alarm_preview = AlarmPreview(self)
        return alarm_preview

    def _init_alert_log(self) -> AlertLog:
        alert_log = AlertLog(self)
        alert_log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return alert_log


class AlarmCard(AlarmCardUI, ExpandableMI, IterableMI):

    def __init__(self, parent: Optional[QWidget]):
        # Properties
        self._alert_active = False
        self._expanded = True

        super().__init__(parent)

        self._init_signals()

    def _init_signals(self):
        def flip():
            self.alert_active = not self.alert_active

        self.alert_log.clicked.connect(flip)
        self.alarm_preview.clicked.connect(self.toggle_expansion)

    @pyqtProperty(bool)
    def alert_active(self) -> bool:
        return self._alert_active

    @alert_active.setter
    def alert_active(self, alert_active: bool) -> None:
        self._alert_active = alert_active
        stylesheet_watcher.update()

    def expansion_changed(self):
        # noinspection PyPropertyAccess
        self.alert_log.setVisible(self.expanded)
        stylesheet_watcher.update()

    def iterable_layout(self) -> QLayout:
        return self.alert_log.layout()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    app.setAttribute(Qt.AA_EnableHighDpiScaling)

    # window = AlarmCard(None)

    window = QWidget()
    window.setAttribute(Qt.WA_StyledBackground, True)
    # window.setStyleSheet("background-color: lightgrey")

    window.setLayout(QVBoxLayout())
    window.layout().addWidget(AlarmCard(parent=window))

    window.show()

    app.exec_()
