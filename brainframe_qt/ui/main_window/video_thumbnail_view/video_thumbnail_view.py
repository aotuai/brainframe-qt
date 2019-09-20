from typing import Dict

# noinspection PyUnresolvedReferences
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimerEvent
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.api.codecs import StreamConfiguration
from brainframe.client.ui.resources import QTAsyncWorker
from brainframe.client.ui.resources.paths import qt_ui_paths


class VideoThumbnailView(QWidget):
    thumbnail_stream_clicked_signal = pyqtSignal(object)
    """Used to alert outer widget of change
    
    Connected to:
    - MainWindow -- QtDesigner
      [parent].show_video_expanded_view()
    - VideoExpandedView -- QtDesigner
      [peer].open_expanded_view_slot()
    """

    def __init__(self, parent=None):

        super().__init__(parent=parent)

        loadUi(qt_ui_paths.video_thumbnail_view_ui, self)

        self.all_stream_confs: Dict[int, StreamConfiguration] = {}
        """Stream IDs currently in the ThumbnailView"""
        self.alert_stream_ids = set()
        """Streams IDs currently in the ThumbnailView with ongoing alerts"""

        self.current_stream_id = None
        """Currently expanded stream. None if no stream selected"""

        self.startTimer(1000)

        # Hide the alerts layout
        self.alert_streams_layout.hide()

    def timerEvent(self, timer_event: QTimerEvent):

        def func():

            stream_configurations = api.get_stream_configurations()
            return stream_configurations

        def callback(stream_configurations):

            received_stream_ids = set()

            # Get all current streams
            for stream_conf in stream_configurations:

                received_stream_ids.add(stream_conf.id)

                if stream_conf.id not in self.all_stream_confs:
                    # Create widgets for each
                    self.new_stream(stream_conf)

            current_stream_ids = self.all_stream_confs.keys()
            dead_stream_ids = current_stream_ids - received_stream_ids

            for stream_id in dead_stream_ids:
                self.delete_stream_slot(self.all_stream_confs[stream_id])

        QTAsyncWorker(self, func, callback).start()

    @pyqtSlot(object)
    def thumbnail_stream_clicked_slot(self, stream_conf):
        """Stream has been clicked

        Connected to:
        - ThumbnailGridLayout -- QtDesigner
          self.alertless_streams_layout.thumbnail_stream_clicked_signal
        - ThumbnailGridLayout -- QtDesigner
          self.alert_streams_layout.thumbnail_stream_clicked_signal
        """

        # Alert outer widget
        # noinspection PyUnresolvedReferences
        self.thumbnail_stream_clicked_signal.emit(stream_conf)

    @pyqtSlot()
    def expand_thumbnail_layouts_slot(self):
        """Expand the grid layouts to fill the entire main_window.

        Connected to:
        - VideoExpandedView -- QtDesigner
          [peer].expanded_stream_closed_signal
        """
        # Resize GridLayout
        self.alertless_streams_layout.expand_grid()
        self.alert_streams_layout.expand_grid()

    @pyqtSlot(object)
    def delete_stream_slot(self, stream_conf):
        """Stream is being deleted

        Connected to:
        - VideoExpandedView -- QtDesigner
          [peer].stream_delete_signal
        """
        # Delete stream from alert widget if it is there
        if stream_conf.id in self.alert_stream_ids:
            self.remove_streams_from_alerts(stream_conf.id)

        del self.all_stream_confs[stream_conf.id]

        video = self.alertless_streams_layout.pop_stream_widget(stream_conf.id)
        video.deleteLater()

    @pyqtSlot(object, bool)
    def ongoing_alerts_slot(self, stream_conf: StreamConfiguration,
                            alerts_ongoing: bool):
        """Alert associated with stream

        Connected to:
        - ThumbnailGridLayout -- QtDesigner
          self.alertless_streams_layout.ongoing_alerts_signal
        - ThumbnailGridLayout -- QtDesigner
          self.alert_streams_layout.ongoing_alerts_signal
        """

        if alerts_ongoing and stream_conf.id not in self.alert_stream_ids:
            self.add_stream_to_alerts(stream_conf.id)

        elif stream_conf.id in self.alert_stream_ids and not alerts_ongoing:
            self.remove_streams_from_alerts(stream_conf.id)

        else:
            message = self.tr("Inconsistent state with alert widgets.")
            raise RuntimeError(message)

    def add_stream_to_alerts(self, stream_id):

        # Expand alert layout if necessary
        if not self.alert_stream_ids:
            self.alert_streams_layout.show()

        # Add stream ID of alert to set
        self.alert_stream_ids.add(stream_id)

        # Move widget from alertless_streams_layout to alert_streams_layout
        widget = self.alertless_streams_layout.pop_stream_widget(stream_id)
        self.alert_streams_layout.add_video(widget)

    def remove_streams_from_alerts(self, stream_id):

        # Remove stream ID of alert from set
        self.alert_stream_ids.remove(stream_id)

        # Hide alert layout if necessary
        if not self.alert_stream_ids:
            self.alert_streams_layout.hide()

        # Move widget from alert_streams_layout to alertless_streams_layout
        widget = self.alert_streams_layout.pop_stream_widget(stream_id)
        self.alertless_streams_layout.add_video(widget)

    def new_stream(self, stream_conf):
        """Create a new stream widget and remember its ID"""
        self.alertless_streams_layout.new_stream_widget(stream_conf)

        # Store ID for each in set
        self.all_stream_confs[stream_conf.id] = stream_conf
