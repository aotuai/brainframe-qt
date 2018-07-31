from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.api.codecs import StreamConfiguration
from brainframe.client.ui.dialogs import TaskConfiguration
from brainframe.client.ui.resources.paths import qt_ui_paths


class VideoExpandedView(QWidget):
    """Holds the expanded video view. Hidden when no stream selected"""

    expanded_stream_closed_signal = pyqtSignal()
    """Signaled when expanded stream is closed
    
    Connected to:
    - MainWindow -- QtDesigner
      [parent].hide_video_expanded_view()
    - VideoThumbnailView -- QtDesigner
      [peer].expand_thumbnail_layouts_slot()
    """

    stream_delete_signal = pyqtSignal(int)
    """Called when the user wants to delete a stream"""

    def __init__(self, parent):
        super().__init__(parent)

        loadUi(qt_ui_paths.video_expanded_view_ui, self)

        self.stream_conf = None

        # TODO(Bryce Beagle): Button is only disabled until API allows editing
        # of StreamConfig
        self.source_config_button.setDisabled(True)

        # https://stackoverflow.com/a/43835396/8134178
        # 3 : 1 height ratio initially
        self.splitter.setSizes([self.height(), self.height() / 3])

    @pyqtSlot(object)
    def open_expanded_view_slot(self, stream_conf: StreamConfiguration):
        """Signaled by thumbnail view when thumbnail video is clicked"""

        self.expanded_video.change_stream(stream_conf)
        self.alert_log.change_stream(stream_conf.id)
        self.stream_conf = stream_conf

        # Set displayed title of stream
        self.stream_name_label.setText(stream_conf.name)

    @pyqtSlot()
    def expanded_stream_closed_slot(self):
        """Signaled by close button"""

        # Stop attempting to display a stream
        self.expanded_video.change_stream(None)

        # Stop alert log from asking for alerts from stream
        self.alert_log.change_stream(None)

        # No more stream_conf associate with
        self.stream_conf = None

        # Alert slots that expanded stream was closed
        # VideoThumbnailView will remove highlight from thumbnail video
        # noinspection PyUnresolvedReferences
        self.expanded_stream_closed_signal.emit()

    @pyqtSlot()
    def delete_stream_button_clicked(self):
        """Delete button has been clicked for stream

        Connected to:
        - QPushButton -- QtDesigner
          self.delete_stream_button.clicked
        """

        # Delete stream from database
        api.delete_stream_configuration(self.stream_conf.id)

        # Remove StreamWidgets associated with stream being deleted
        # noinspection PyUnresolvedReferences
        self.stream_delete_signal.emit(self.stream_conf.id)

        self.expanded_stream_closed_slot()
        self.stream_conf = None

    @pyqtSlot()
    def open_task_config(self):
        print("Opening task configuration")
        config = TaskConfiguration.open_configuration(self.stream_conf)
        if not config:
            return

            # TODO(Bryce Beagle): Actually say what this TODO is for
            # TODO

    @pyqtSlot()
    def open_source_config(self):
        # TODO(Bryce Beagle): Open the source config dialog window for the
        # stream
        # Use ui.dialogs.stream_configuration
        print("Opening source configuration")
