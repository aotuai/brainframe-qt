# noinspection PyUnresolvedReferences
# pyqtProperty is erroneously detected as unresolved
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from brainframe.client.api import api
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

        self.all_stream_ids = set()
        """Stream IDs currently in the ThumbnailView"""
        self.alert_stream_ids = set()
        """Streams IDs currently in the ThumbnailView with ongoing alerts"""

        self.current_stream_id = None
        """Currently expanded stream. None if no stream selected"""

        # Get all current streams
        for stream_conf in api.get_stream_configurations():

            # Create widgets for each
            self.new_stream(stream_conf)

    @pyqtSlot(object)
    def thumbnail_stream_clicked_slot(self, stream_conf):
        """Stream has been clicked

        Connected to:
        - ThumbnailGridLayout -- QtDesigner
          self.all_streams_layout.thumbnail_stream_clicked_signal
        - ThumbnailGridLayout -- QtDesigner
          self.alert_streams_layout.thumbnail_stream_clicked_signal
        """

        # Alert outer widget
        self.thumbnail_stream_clicked_signal.emit(stream_conf)

    @pyqtSlot()
    def expand_thumbnail_layouts_slot(self):
        """Expand the grid layouts to fill the entire main_window.

        Connected to:
        - VideoExpandedView -- QtDesigner
          [peer].expanded_stream_closed_signal
        """
        # Resize GridLayout
        self.all_streams_layout.expand_grid()
        self.alert_streams_layout.expand_grid()

    @pyqtSlot(int)
    def delete_stream_slot(self, stream_id: int):
        """Stream is being deleted

        Connected to:
        - VideoExpandedView -- QtDesigner
          [peer].stream_delete_signal
        """
        self.all_streams_layout.delete_stream_widget(stream_id)

        # Delete stream from alert widget if it is there
        if stream_id in self.alert_stream_ids:
            self.alert_streams_layout.delete_stream_widget(stream_id)

    @pyqtSlot(object, bool)
    def ongoing_alerts_slot(self, stream_conf, alerts_ongoing):
        """Alert associated with stream

        Connected to:
        - ThumbnailGridLayout -- QtDesigner
          self.all_streams_layout.ongoing_alerts_signal
        """

        print("JHERE")

        if alerts_ongoing and stream_conf.id not in self.alert_stream_ids:

            print("SDSDS")

            # Expand alert layout if necessary
            # if self.alert_stream_ids:
            #     self.alert_streams_container.setVisible()

            # Add stream ID of alert to set
            self.alert_stream_ids.add(stream_conf.id)

            # Create a widget for stream in the alert layout
            self.alert_streams_layout.new_stream_widget(stream_conf)

        elif stream_conf.id in self.alert_stream_ids and not alerts_ongoing:

            # Remove stream ID of alert from set
            self.alert_stream_ids.remove(stream_conf.id)

            # Hide alert layout if necessary
            if not self.alert_stream_ids:
                self.alert_streams_container.hide()

            # Remove widget for stream in the alert layout
            self.alert_streams_layout.delete_stream_widget(stream_conf.id)

        else:
            raise RuntimeError("Inconsistent state with alert widgets")

    def new_stream(self, stream_conf):
        """Create a new stream widget and remember its ID"""
        self.all_streams_layout.new_stream_widget(stream_conf)

        # Store ID for each in set
        self.all_stream_ids.add(stream_conf.id)