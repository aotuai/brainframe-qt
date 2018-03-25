# noinspection PyUnresolvedReferences
# pyqtProperty is erroneously detected as unresolved
from PyQt5.QtCore import pyqtProperty, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from visionapp.client.api import api

from visionapp.client.ui.dialogs import StreamConfigurationDialog
from visionapp.client.ui.resources.paths import qt_ui_paths, image_paths
from .video_small.video_small import VideoSmall


class VideoThumbnailView(QWidget):
    thumbnail_stream_clicked_signal = pyqtSignal(object)
    """Used to alert outer widget of change"""

    def __init__(self, parent=None, grid_width=3):

        # TODO: Debug
        if api is not None:
            api.get_stream_configurations = get_stream_configurations_debug

        super().__init__(parent)

        loadUi(qt_ui_paths.video_thumbnail_view_ui, self)

        self._grid_width = grid_width
        self._grid_width_expanded = grid_width

        self.streams = {}
        if api is not None:
            for stream_conf in api.get_stream_configurations():
                self.new_stream_widget(stream_conf)
        else:
            # Create fake videos for QtDesigner
            # TODO: Use mock for this
            for stream_conf in get_stream_configurations_debug():
                self.new_stream_widget(stream_conf)

        self.current_stream_id = None

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

        self.grid_width = 1

    @pyqtSlot()
    def expand_thumbnail_view_slot(self):
        """Called by outer widget when expanded video is explicitly closed

        Removes selection border from currently selected video
        """
        # Resize GridLayout
        self.grid_width = self._grid_width_expanded

        # Remove selection border from currently selected video
        if self.current_stream_id:
            self.streams[self.current_stream_id].remove_selection_border()

    @pyqtSlot()
    def create_new_stream_slot(self):
        stream_conf = StreamConfigurationDialog.configure_stream()

        if stream_conf:
            self.new_stream_widget(stream_conf)

    @pyqtProperty(int)
    def grid_width(self):
        return self._grid_width

    @grid_width.setter
    def grid_width(self, grid_width):
        self._grid_width = grid_width

        widgets = []
        for i in reversed(range(self.main_layout.count())):
            widgets.insert(0, self.main_layout.itemAt(i).widget())
            self.main_layout.removeItem(self.main_layout.itemAt(i))

        for widget in widgets:
            self._add_widget_to_layout(widget)

        self.updateGeometry()

        self._set_layout_equal_stretch()

    def new_stream_widget(self, stream_conf):
        video = VideoSmall(self, stream_conf, 30)
        self.streams[stream_conf.id] = video
        self._add_widget_to_layout(video)

    def _add_widget_to_layout(self, widget):
        row, col = divmod(self.main_layout.count(), self._grid_width)

        self.main_layout.addWidget(widget, row, col)

        self._set_layout_equal_stretch()

    def _set_layout_equal_stretch(self):
        """Set all cells in grid layout to have have same width and height"""
        for row in range(self.main_layout.rowCount()):
            self.main_layout.setRowStretch(row, 1)
        for col in range(self.main_layout.columnCount()):
            self.main_layout.setColumnStretch(col, 1)

    def resizeEvent(self, event):
        print(self.width())
        super().resizeEvent(event)


# DEBUG
def get_stream_configurations_debug():
    from visionapp.client.api.codecs import StreamConfiguration
    configs = [
        StreamConfiguration(name="Image1",
                            connection_type=StreamConfiguration.ConnType.file,
                            parameters=
                            f'{{"filepath": "{image_paths.cat_test_video}"}}',
                            id_=1010101),
        StreamConfiguration(name="Image1",
                            connection_type=StreamConfiguration.ConnType.file,
                            parameters=
                            f'{{"filepath": "{image_paths.camera_test_video}"}}',
                            id_=2020202),
        StreamConfiguration(name="Image1",
                            connection_type=StreamConfiguration.ConnType.file,
                            parameters=
                            f'{{"filepath":"{image_paths.ostrich_test_video}"}}',
                            id_=3030303),
        StreamConfiguration(name="Image1",
                            connection_type=StreamConfiguration.ConnType.file,
                            parameters=
                            f'{{"filepath": "{image_paths.camera_test_video}"}}',
                            id_=4040404)]

    return configs
