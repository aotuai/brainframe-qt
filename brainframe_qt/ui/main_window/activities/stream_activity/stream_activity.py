from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget

from brainframe_qt.extensions import WindowedActivity
from .stream_view import StreamView


class StreamActivity(WindowedActivity):
    _built_in = True

    @staticmethod
    def icon() -> QIcon:
        return QIcon(":/icons/stream_toolbar")

    @staticmethod
    def main_widget(*, parent: QWidget) -> QWidget:
        return StreamView(parent)

    @staticmethod
    def short_name() -> str:
        return QApplication.translate("StreamActivity", "Streams")
