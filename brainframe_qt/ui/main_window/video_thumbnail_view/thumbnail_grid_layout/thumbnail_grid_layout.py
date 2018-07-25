# noinspection PyUnresolvedReferences
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QGridLayout, QWidget

from .video_small.video_small import VideoSmall


class ThumbnailGridLayout(QWidget):
    thumbnail_stream_clicked_signal = pyqtSignal(object)

    ongoing_alerts_signal = pyqtSignal(object, bool)
    """Alert the thumbnail view that a stream has an alert associated with it
    
    Only all_alerts_layout instance has this signal connected to the slot
        
    Connected to:
    - VideoThumbnailView -- QtDesigner
      [parent].ongoing_alerts_slot
    """

    def __init__(self, parent=None, grid_num_columns=3):
        super().__init__(parent=parent)

        self.setLayout(QGridLayout())

        self.grid_num_rows = 0
        """Current number of row in grid"""
        self._grid_num_columns = grid_num_columns
        """Current number of columns in grid"""
        self._grid_num_columns_expanded = grid_num_columns
        """Number of columns in grid when thumbnail view is expanded"""

        self.stream_widgets = {}
        """Streams currently in the ThumbnailGridLayout

        Dict is formatted as {stream_id: VideoSmall()}
        """

        self.current_stream_id = None
        """Currently expanded stream. None if no stream selected"""

    def new_stream_widget(self, stream_conf):
        video = VideoSmall(self, stream_conf, 30)

        self.stream_widgets[stream_conf.id] = video
        self._add_widget_to_layout(video)

        self._connect_widget_signals(video)

        self._set_layout_equal_stretch()

    def _add_widget_to_layout(self, widget):
        row, col = divmod(self.layout().count(), self._grid_num_columns)

        self.layout().addWidget(widget, row, col)

        # row+1 is equal to number of rows in grid after addition
        # (+1 is for indexing at 1 for a count)
        self.grid_num_rows = row + 1

    def _connect_widget_signals(self, widget: VideoSmall):
        """Connect the stream widget's signal(s) to the grid and to the parent
        view
        """
        # Because the widgets are added dynamically, we can't connect slots
        # and signals using QtDesigner and have to do it manually
        widget.stream_clicked.connect(self.thumbnail_stream_clicked_slot)
        widget.ongoing_alerts_signal.connect(self.ongoing_alerts_slot)

    @pyqtSlot(object)
    def thumbnail_stream_clicked_slot(self, stream_conf):
        """Signaled by child VideoWidget and then passed upwards"""
        # Resize layout to be a single column
        self.grid_num_columns = 1

        # Alert outer widgets and peers if called from child
        if isinstance(self.sender(), VideoSmall):
            self.thumbnail_stream_clicked_signal.emit(stream_conf)

            # Store stream as current stream
            self.current_stream_id = stream_conf.id

    @pyqtSlot(bool)
    def ongoing_alerts_slot(self, alerts_ongoing: bool):
        """Called by child stream widget when it has an ongoing alert

        Connected to:
        - VideoSmall -- Dynamic
          [child].ongoing_alerts_signal
        """
        stream_conf = self.sender().stream_conf
        # noinspection PyUnresolvedReferences
        self.ongoing_alerts_signal.emit(stream_conf, alerts_ongoing)

    def _set_layout_equal_stretch(self):
        """Set all cells in grid layout to have have same width and height"""
        for row in range(self.layout().rowCount()):
            if row < self.grid_num_rows:
                self.layout().setRowStretch(row, 1)
            else:
                # Hide rows that have nothing in them
                self.layout().setRowStretch(row, 0)

        # Force the minimum number of shown columns to be equal to exactly
        # self._grid_num_columns.
        # If self._grid_num_columns > columnCount(), force show extra columns
        # If self._grid_num_columns < columnCount(), force hide extra columns
        num_cols = max(self.layout().columnCount(), self._grid_num_columns)
        for col in range(num_cols):
            if col < self._grid_num_columns:
                self.layout().setColumnStretch(col, 1)
            else:
                # Hide columns that have nothing in them
                self.layout().setColumnStretch(col, 0)

    def delete_stream_widget(self, stream_id):
        """Delete widget in layout with stream id = stream_id"""

        stream_widget = self.stream_widgets.pop(stream_id)
        self.layout().removeWidget(stream_widget)
        stream_widget.deleteLater()

        # Force a reflow in case it hasn't happened yet
        self.grid_num_columns = self._grid_num_columns

        # Streams can currently only be deleted when they're selected (that's
        # where the button is). Therefore, current_stream_id will always need to
        # be set to None
        self.current_stream_id = None

    @pyqtProperty(int)
    def grid_num_columns(self):
        return self._grid_num_columns

    @grid_num_columns.setter
    def grid_num_columns(self, grid_num_columns):
        self._grid_num_columns = grid_num_columns

        widgets = []
        for i in reversed(range(self.layout().count())):
            widgets.insert(0, self.layout().itemAt(i).widget())
            self.layout().removeItem(self.layout().itemAt(i))

        for widget in widgets:
            self._add_widget_to_layout(widget)

        self._set_layout_equal_stretch()

    def expand_grid(self):
        """Called by outer widget when expanded video is explicitly closed

        TODO: Unimplemented
        Removes selection border from currently selected video
        """
        # Resize GridLayout
        self.grid_num_columns = self._grid_num_columns_expanded

        # Remove selection border from currently selected video
        if self.current_stream_id:
            self.stream_widgets[
                self.current_stream_id
            ].remove_selection_border()
