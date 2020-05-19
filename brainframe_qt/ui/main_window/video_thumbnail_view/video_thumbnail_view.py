from typing import Dict, List

from PyQt5.QtCore import QMetaObject, QThread, Q_ARG, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from brainframe.client.api_utils import api
from brainframe.api.bf_codecs import StreamConfiguration
from brainframe.client.api_utils.zss_pubsub import zss_publisher
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

        self._streams_being_added = set()
        """Streams that are currently being added on another thread"""

        self.current_stream_id = None
        """Currently expanded stream. None if no stream selected"""

        # Hide the alerts layout
        self.alert_streams_layout.hide()

        self._init_pubsub()

    def _init_pubsub(self) -> None:
        sub = zss_publisher.subscribe_streams(self._handle_stream_stream)
        self.destroyed.connect(lambda: zss_publisher.unsubscribe(sub))

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

    def delete_stream(self, stream_id: int) -> None:
        """Delete a stream from the view"""

        # Delete stream from alert widget if it is there
        if stream_id in self.alert_stream_ids:
            self.remove_streams_from_alerts(stream_id)

        del self.all_stream_confs[stream_id]

        video = self.alertless_streams_layout.pop_stream_widget(stream_id)
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

    def new_stream(self, stream_id: int) -> None:
        """Create a new stream widget and remember its ID"""

        # Don't do anything if we're already in the process of adding this
        # stream
        if stream_id in self._streams_being_added:
            return
        else:
            self._streams_being_added.add(stream_id)

        def on_success(stream_conf):
            self.alertless_streams_layout.new_stream_widget(stream_conf)

            # Store ID for each in set
            self.all_stream_confs[stream_conf.id] = stream_conf

            self._streams_being_added.remove(stream_id)

        def on_error(exc: BaseException):
            self._streams_being_added.remove(stream_id)
            raise exc

        QTAsyncWorker(self, api.get_stream_configuration, f_args=(stream_id,),
                      on_success=on_success, on_error=on_error) \
            .start()

    @pyqtSlot(object)
    def _handle_stream_stream(
            self, stream_confs: List[StreamConfiguration]) \
            -> None:
        """Handles the stream of StreamConfiguration information from the
        pubsub system"""

        if QThread.currentThread() != self.thread():
            # Move to the UI Thread
            QMetaObject.invokeMethod(self,
                                     self._handle_stream_stream.__name__,
                                     Qt.QueuedConnection,
                                     Q_ARG("PyQt_PyObject", stream_confs))
            return

        received_stream_ids = {stream_conf.id for stream_conf in stream_confs}
        current_stream_ids = self.all_stream_confs.keys()

        new_stream_ids = received_stream_ids - current_stream_ids
        dead_stream_ids = current_stream_ids - received_stream_ids

        for stream_id in new_stream_ids:
            self.new_stream(stream_id)

        for stream_id in dead_stream_ids:
            self.delete_stream(stream_id)
