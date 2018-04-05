# noinspection PyUnresolvedReferences
# pyqtProperty is erroneously detected as unresolved
from PyQt5.QtCore import pyqtProperty, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QAction, QGridLayout, QMessageBox, QWidget
from PyQt5.uic import loadUi

from visionapp.client.api import api, APIError

from .video_small.video_small import VideoSmall
from visionapp.client.ui.dialogs import StreamConfigurationDialog
from visionapp.client.ui.resources.paths import qt_ui_paths
from visionapp.shared import rest_errors

class VideoThumbnailView(QWidget):
    thumbnail_stream_clicked_signal = pyqtSignal(object)
    """Used to alert outer widget of change"""

    def __init__(self, parent=None, grid_num_columns=3):

        super().__init__(parent)

        loadUi(qt_ui_paths.video_thumbnail_view_ui, self)

        self.grid_num_rows = 0
        """Current number of row in grid"""
        self._grid_num_columns = grid_num_columns
        """Current number of columns in grid"""
        self._grid_num_columns_expanded = grid_num_columns
        """Number of columns in grid when thumbnail view is expanded"""

        self.streams = {}
        """Streams currently in the ThumbnailView
        
        Dict is formatted as {stream_id: VideoSmall()}
        """

        for stream_conf in api.get_stream_configurations():
            self.new_stream_widget(stream_conf)

        self.current_stream_id = None
        """Currently expanded stream. None if no stream selected"""

    @pyqtSlot(int)
    def thumbnail_stream_clicked_slot(self, stream_id):
        """Signaled by child VideoWidget and then passed upwards

        Also removes selection border from previously selected video"""
        print(f"Stream {stream_id} clicked")

        # TODO: Don't do anything if stream already active
        # if self.current_stream_id == stream_id:
        #     return

        # Remove selection border from previously selected video
        if self.current_stream_id:
            self.streams[self.current_stream_id].remove_selection_border()

        # Alert outer widget
        self.thumbnail_stream_clicked_signal.emit(
            self.streams[stream_id].stream_conf)

        # Store stream as current stream
        self.current_stream_id = stream_id

        self.grid_num_columns = 1

    @pyqtSlot()
    def expand_thumbnail_view_slot(self):
        """Called by outer widget when expanded video is explicitly closed

        Removes selection border from currently selected video
        """
        # Resize GridLayout
        self.grid_num_columns = self._grid_num_columns_expanded

        # Remove selection border from currently selected video
        if self.current_stream_id:
            self.streams[self.current_stream_id].remove_selection_border()

    @pyqtSlot(QAction)
    def create_new_stream_slot(self, action):
        stream_conf = StreamConfigurationDialog.configure_stream()
        if stream_conf is None: return
        try:
            stream_conf = api.set_stream_configuration(stream_conf)

            # Currently, we default to setting all new streams as 'active'
            api.start_analyzing(stream_conf.id)

        except APIError as err:

            if err.kind == rest_errors.DUPLICATE_STREAM_SOURCE:
                message = "<b>Stream source already open</b>" \
                          "<br><br>" \
                          "You already have the stream source open.<br><br>" \
                          "Error: <b>" + err.kind + "</b>"
            else:
                message = "<b>Error encountered while opening stream</b>" \
                          "<br><br>" \
                          "Is stream already open?<br>" \
                          "Is this a valid stream source?<br><br>" \
                          "Error: <b>" + err.kind + "</b>"

            QMessageBox.information(self, "Error Opening Stream", message)
            return

        self.new_stream_widget(stream_conf)

    @pyqtSlot(int)
    def delete_stream_slot(self, stream_id):
        """"""
        api.delete_stream_configuration(stream_id)
        self.current_stream_id = None

        stream_widget = self.streams.pop(stream_id)
        self.main_layout.removeWidget(stream_widget)
        stream_widget.deleteLater()

        # Force a reflow in case it hasn't happened yet
        self.grid_num_columns = self._grid_num_columns

    @pyqtProperty(int)
    def grid_num_columns(self):
        return self._grid_num_columns

    @grid_num_columns.setter
    def grid_num_columns(self, grid_num_columns):
        self._grid_num_columns = grid_num_columns

        widgets = []
        for i in reversed(range(self.main_layout.count())):
            widgets.insert(0, self.main_layout.itemAt(i).widget())
            self.main_layout.removeItem(self.main_layout.itemAt(i))

        for widget in widgets:
            self._add_widget_to_layout(widget)

        self._set_layout_equal_stretch()

    def new_stream_widget(self, stream_conf):
        video = VideoSmall(self, stream_conf, 30)
        self.streams[stream_conf.id] = video
        self._add_widget_to_layout(video)
        self._set_layout_equal_stretch()

    def _add_widget_to_layout(self, widget):
        row, col = divmod(self.main_layout.count(), self._grid_num_columns)

        self.main_layout.addWidget(widget, row, col)

        # row+1 is equal to number of rows in grid after addition
        # (+1 is for indexing at 1 for a count)
        self.grid_num_rows = row+1

    def _set_layout_equal_stretch(self):
        """Set all cells in grid layout to have have same width and height"""
        for row in range(self.main_layout.rowCount()):
            if row < self.grid_num_rows:
                self.main_layout.setRowStretch(row, 1)
            else:
                # Hide rows that have nothing in them
                self.main_layout.setRowStretch(row, 0)
        for col in range(self.main_layout.columnCount()):
            if col < self._grid_num_columns:
                self.main_layout.setColumnStretch(col, 1)
            else:
                # Hide columns that have nothing in them
                self.main_layout.setColumnStretch(col, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
