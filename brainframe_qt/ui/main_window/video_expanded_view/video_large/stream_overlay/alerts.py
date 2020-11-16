from abc import ABC, abstractmethod

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication


class AbstractOverlayAlert(ABC):

    @abstractmethod
    def short_text(self) -> str:
        ...

    @abstractmethod
    def long_text(self) -> str:
        ...

    @abstractmethod
    def icon(self) -> QIcon:
        ...


class _NoAnalysisAlert(AbstractOverlayAlert):

    def short_text(self) -> str:
        return QApplication.translate("OverlayAlert", "Awaiting analysis")

    def long_text(self) -> str:
        return QApplication.translate(
            "OverlayAlert",
            "No analysis results have been received for this stream yet"
        )

    def icon(self) -> QIcon:
        return QIcon(":/icons/analysis_error")


class _DesyncedAnalysisAlert(AbstractOverlayAlert):
    def short_text(self) -> str:
        return QApplication.translate("OverlayAlert", "Desynced Analysis")

    def long_text(self) -> str:
        message_text1 = QApplication.translate(
            "OverlayAlert",
            "The server is not processing frames quickly enough.")
        message_text2 = QApplication.translate(
            "OverlayAlert",
            "Low analysis FPS will cause detections to appear before their "
            + "frames.")
        message_text = f"{message_text1}<br>{message_text2}"

        return message_text

    def icon(self) -> QIcon:
        return QIcon(":/icons/analysis_error")


class _BufferFullAlert(AbstractOverlayAlert):
    def short_text(self) -> str:
        return QApplication.translate(
            "OverlayAlert",
            "Severely desynced analysis"
        )

    def long_text(self) -> str:
        message_text1 = QApplication.translate(
            "OverlayAlert",
            "The server is processing frames extremely slowly.")
        message_text2 = QApplication.translate(
            "OverlayAlert",
            "Results will not appear synced with the frames they correspond "
            + "to.")
        message_text = f"{message_text1}<br>{message_text2}"

        return message_text

    def icon(self) -> QIcon:
        return QIcon(":/icons/analysis_error")


NO_ANALYSIS_ALERT = _NoAnalysisAlert()
DESYNCED_ANALYSIS_ALERT = _DesyncedAnalysisAlert()
BUFFER_FULL_ALERT = _BufferFullAlert()
