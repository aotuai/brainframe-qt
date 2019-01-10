# noinspection PyUnresolvedReferences
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
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

        # Hide the alerts layout
        self.alert_streams_layout.hide()

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
            self.remove_streams_from_alerts(stream_conf)
        else:
            self.alertless_streams_layout.delete_stream_widget(stream_conf.id)

    @pyqtSlot(object, bool)
    def ongoing_alerts_slot(self, stream_conf, alerts_ongoing):
        """Alert associated with stream

        Connected to:
        - ThumbnailGridLayout -- QtDesigner
          self.alertless_streams_layout.ongoing_alerts_signal
        - ThumbnailGridLayout -- QtDesigner
          self.alert_streams_layout.ongoing_alerts_signal
        """

        if alerts_ongoing and stream_conf.id not in self.alert_stream_ids:

            self.add_stream_to_alerts(stream_conf)
            self.alertless_streams_layout.delete_stream_widget(stream_conf.id)

        elif stream_conf.id in self.alert_stream_ids and not alerts_ongoing:

            self.remove_streams_from_alerts(stream_conf)
            self.alertless_streams_layout.new_stream_widget(stream_conf)

        else:
            raise RuntimeError("Inconsistent state with alert widgets")

    def add_stream_to_alerts(self, stream_conf):

        # Expand alert layout if necessary
        if not self.alert_stream_ids:
            self.alert_streams_layout.show()

        # Add stream ID of alert to set
        self.alert_stream_ids.add(stream_conf.id)

        # Create a widget for stream in the alert layout
        self.alert_streams_layout.new_stream_widget(stream_conf)

    def remove_streams_from_alerts(self, stream_conf):

        # Remove stream ID of alert from set
        self.alert_stream_ids.remove(stream_conf.id)

        # Hide alert layout if necessary
        if not self.alert_stream_ids:
            self.alert_streams_layout.hide()

        # Remove widget for stream in the alert layout
        self.alert_streams_layout.delete_stream_widget(stream_conf.id)

    def new_stream(self, stream_conf):
        """Create a new stream widget and remember its ID"""
        self.alertless_streams_layout.new_stream_widget(stream_conf)

        # Store ID for each in set
        self.all_stream_ids.add(stream_conf.id)

    def resizeEvent(self, event):
        """Prevent the scrollbar from appearing and disappearing as the
        contents of the scroll area try to fill the width
        """
        super().resizeEvent(event)

        magic = 2
        """Arbitrary value because the scrollbar width was _just_ not big
        enough, most likely because h+w calculation isn't exactly the right
        thing. This value was handpicked."""

        h = self.hack_widget_used_to_make_videos_stay_at_top_of_widget.height()

        # If the height of the widget at the bottom is small, that means we're
        # either max height w/o scrollbar (the problem case) or >max height,
        # where the scrollbar is always on. Regardless, we want the scrollbar
        # on
        if h <= self.thumbnail_scroll_area.verticalScrollBar().width() + magic:
            self.thumbnail_scroll_area.setVerticalScrollBarPolicy(
                Qt.ScrollBarAlwaysOn)
        # Otherwise, hide the scrollbar
        else:
            self.thumbnail_scroll_area.setVerticalScrollBarPolicy(
                Qt.ScrollBarAlwaysOff)
