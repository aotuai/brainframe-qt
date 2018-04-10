from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from visionapp.client.api.codecs import StreamConfiguration
from visionapp.client.ui.dialogs import TaskConfiguration
from visionapp.client.ui.resources.paths import qt_ui_paths


class VideoExpandedView(QWidget):
    """Holds the expanded video view. Hidden when no stream selected"""

    expanded_stream_closed_signal = pyqtSignal()
    """Signaled when expanded stream is closed"""

    stream_delete_signal = pyqtSignal(int)
    """Called when the user wants to delete a stream"""

    def __init__(self, parent):
        super().__init__(parent)

        loadUi(qt_ui_paths.video_expanded_view_ui, self)

        self.stream_conf = None

        # TODO: Button is only disabled until API allows editing of StreamConfig
        self.source_config_button.setDisabled(True)

        self._set_widgets_hidden(True)

    @pyqtSlot(object)
    def open_expanded_view_slot(self, stream_conf: StreamConfiguration):
        """Signaled by thumbnail view when thumbnail video is clicked"""

        self.expanded_video.change_stream(stream_conf)
        self.alert_log.change_stream(stream_conf.id)
        self.stream_conf = stream_conf

        # Show expanded view widgets
        self.stream_name_label.setText(stream_conf.name)
        self._set_widgets_hidden(False)

    @pyqtSlot()
    def expanded_stream_closed_slot(self):
        """Signaled by close button"""

        self.expanded_video.change_stream(None)
        self.alert_log.change_stream(None)
        self.stream_conf = None

        # Hide expanded view widgets
        self._set_widgets_hidden(True)

        # Alert slots that expanded stream was closed
        # VideoThumbnailView will remove highlight from thumbnail video
        self.expanded_stream_closed_signal.emit()

    @pyqtSlot()
    def delete_stream_button_clicked(self):
        self.stream_delete_signal.emit(self.stream_conf.id)
        self.expanded_video.change_stream(None)
        self.alert_log.change_stream(None)
        self.expanded_stream_closed_slot()
        self.stream_conf = None

    @pyqtSlot()
    def open_task_config(self):
        print("Opening task configuration")
        config = TaskConfiguration.open_configuration(self.stream_conf)
        if not config:
            return

            # TODO

    @pyqtSlot()
    def open_source_config(self):
        # TODO: Alex: Open the source config dialog window for the stream
        # Use ui.dialogs.stream_configuration
        print("Opening source configuration")

    def _set_widgets_hidden(self, hidden=True):
        self.expanded_video.setHidden(hidden)
        self.hide_button.setHidden(hidden)
        self.alert_log.setHidden(hidden)
        self.task_config_button.setHidden(hidden)
        self.source_config_button.setHidden(hidden)
        self.stream_name_label.setHidden(hidden)
        self.delete_stream_button.setHidden(hidden)
