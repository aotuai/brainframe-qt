from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from brainframe.client.ui.resources import stylesheet_watcher
from brainframe.client.ui.resources.alarms.alarm_bundle import AlarmBundle
from brainframe.client.ui.resources.paths import qt_qss_paths


class AlarmViewUI(QScrollArea):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.container_widget = self._init_container_widget()
        self._init_viewport_widget()

        self._init_layout()

        self.setWidget(self.container_widget)

        self._init_style()

    def _init_layout(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.setAlignment(Qt.AlignTop)

        self.container_widget.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.container_widget.setAttribute(Qt.WA_StyledBackground, True)

        self.setWidgetResizable(True)

        stylesheet_watcher.watch(self, qt_qss_paths.alarm_view_qss)

    def _init_container_widget(self) -> QWidget:
        container_widget = QWidget(self)
        container_widget.setObjectName("container")
        return container_widget

    def _init_viewport_widget(self) -> None:
        # Give the viewport a name for the stylesheet
        self.viewport().setObjectName("viewport")


class AlarmView(AlarmViewUI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        for _ in range(3):
            self.add_alarm_bundle()

    def add_alarm_bundle(self):
        self.container_widget.layout().addWidget(AlarmBundle(self))


if __name__ == '__main__':
    import typing
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    app.setAttribute(Qt.AA_EnableHighDpiScaling)

    window = QWidget()
    window.setAttribute(Qt.WA_StyledBackground, True)

    window.setLayout(QVBoxLayout())
    window.layout().addWidget(AlarmView(typing.cast(QWidget, None)))

    window.show()

    app.exec_()
