# noinspection PyUnresolvedReferences
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from brainframe.client.api.codecs import StreamConfiguration
from brainframe.client.ui.resources.paths import qt_ui_paths
from .video_small.video_small import VideoSmall


class ThumbnailGridLayout(QWidget):
    thumbnail_stream_clicked_signal = pyqtSignal(object)

    ongoing_alerts_signal = pyqtSignal(object, bool)
    """Alert the thumbnail view that a stream has an alert associated with it
        
    Connected to:
    - VideoThumbnailView -- QtDesigner
      [parent].ongoing_alerts_slot
    """

    def __init__(self, parent=None, grid_num_columns=3):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.thumbnail_grid_layout_ui, self)

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

        self._layout_name: str = "Grid Layout"
        """Text displayed on label on widget above grid"""

        # Toggle the expansion of the streams when the button is clicked
        self.dropdown_button.clicked.connect(self.toggle_expansion)

        self._init_style()

    def new_stream_widget(self, stream_conf: StreamConfiguration):
        video = VideoSmall(self, stream_conf)
        self.add_video(video)

        self._connect_widget_signals(video)

    def add_video(self, video):

        self.stream_widgets[video.stream_conf.id] = video
        self._add_widget_to_layout(video)

        self._set_layout_equal_stretch()

    def _add_widget_to_layout(self, widget):
        row, col = divmod(self.grid_layout.count(), self._grid_num_columns)

        self.grid_layout.addWidget(widget, row, col)

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
        """Signaled by child VideoWidget and then passed upwards

        Connected to:
        - VideoSmall -- Dynamic
          [child].stream_clicked
        - ThumbnailGridLayout -- QtDesigner
          [peer].thumbnail_stream_clicked_signal
        """
        # Resize layout to be a single column
        self.grid_num_columns = 1

        # Alert outer widgets and peers if called from child
        if isinstance(self.sender(), VideoSmall):
            self.thumbnail_stream_clicked_signal.emit(stream_conf)

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
        for row in range(self.grid_layout.rowCount()):
            if row < self.grid_num_rows:
                self.grid_layout.setRowStretch(row, 1)
            else:
                # Hide rows that have nothing in them
                self.grid_layout.setRowStretch(row, 0)

        # Force the minimum number of shown columns to be equal to exactly
        # self._grid_num_columns.
        # If self._grid_num_columns > columnCount(), force show extra columns
        # If self._grid_num_columns < columnCount(), force hide extra columns
        num_cols = max(self.grid_layout.columnCount(), self._grid_num_columns)
        for col in range(num_cols):
            if col < self._grid_num_columns:
                self.grid_layout.setColumnStretch(col, 1)
            else:
                # Hide columns that have nothing in them
                self.grid_layout.setColumnStretch(col, 0)

    def pop_stream_widget(self, stream_id) -> VideoSmall:
        """Remove widget with stream id = stream_id from layout and return
        it"""

        stream_widget = self.stream_widgets.pop(stream_id)
        self.grid_layout.removeWidget(stream_widget)

        # Force a reflow in case it hasn't happened yet
        self.grid_num_columns = self._grid_num_columns

        return stream_widget

    def expand_grid(self, expand: bool):
        """Called by outer widget when expanded video is explicitly closed"""

        if expand:
            num_columns = self._grid_num_columns_expanded
        else:
            num_columns = 1

        self.grid_num_columns = num_columns

    @pyqtSlot(bool)
    def toggle_expansion(self, expand):
        """Called when the dropdown button bar is clicked

        Connected to:
        - QToolButton -- Dynamic
          [self].dropdown_button.clicked
        """
        arrow_type = Qt.DownArrow if expand else Qt.RightArrow
        self.dropdown_button.setArrowType(arrow_type)

        self.layout_container.setVisible(expand)

    @pyqtProperty(int)
    def grid_num_columns(self):
        return self._grid_num_columns

    @grid_num_columns.setter
    def grid_num_columns(self, grid_num_columns):
        self._grid_num_columns = grid_num_columns

        widgets = []
        for i in reversed(range(self.grid_layout.count())):
            widgets.insert(0, self.grid_layout.itemAt(i).widget())
            self.grid_layout.removeItem(self.grid_layout.itemAt(i))

        for widget in widgets:
            self._add_widget_to_layout(widget)

        self._set_layout_equal_stretch()

    @pyqtProperty(str)
    def layout_name(self):
        return self._layout_name

    @layout_name.setter
    def layout_name(self, layout_name):
        self.dropdown_button.setText(layout_name)
        self._layout_name = layout_name

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)
