from PyQt5.QtCore import pyqtSignal, pyqtSlot, QEvent, QTimerEvent
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.api.codecs import StreamConfiguration
from brainframe.client.ui.dialogs import PluginConfigDialog, TaskConfiguration
from brainframe.client.ui.resources import QTAsyncWorker
from brainframe.client.ui.resources.paths import qt_ui_paths
from brainframe.client.ui.resources.ui_elements.buttons import FloatingXButton


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

    stream_delete_signal = pyqtSignal(object)
    """Called when the user wants to delete a stream"""

    def __init__(self, parent):
        super().__init__(parent)

        loadUi(qt_ui_paths.video_expanded_view_ui, self)

        self.hide_button: FloatingXButton = None

        self.stream_conf = None

        self._init_ui()

        self.timer: int = None

    def _init_ui(self):
        # https://stackoverflow.com/a/43835396/8134178
        # 3 : 1 height ratio initially
        self.splitter.setSizes([self.height(), self.height() / 3])

        self.hide_button = FloatingXButton(self, self.palette().mid(),
                                           m_top=15, m_right=15)
        self.hide_button.hide()
        self.hide_button.setToolTip(self.tr("Close expanded video view"))
        # noinspection PyUnresolvedReferences
        self.hide_button.clicked.connect(self.expanded_stream_closed_slot)

    # noinspection PyPep8Naming
    def enterEvent(self, event: QEvent):
        self.hide_button.show()
        super().enterEvent(event)

    # noinspection PyPep8Naming
    def leaveEvent(self, event: QEvent):
        self.hide_button.hide()
        super().leaveEvent(event)

    def timerEvent(self, timer_event: QTimerEvent):
        """Close the expanded view if the currently open stream no longer
        exists on the server"""
        def func():

            stream_configurations = api.get_stream_configurations()
            return stream_configurations

        def callback(stream_configurations):

            for stream_conf in stream_configurations:
                if self.stream_conf.id == stream_conf.id:
                    return
            self.expanded_stream_closed_slot()

        QTAsyncWorker(self, func, callback).start()

    @pyqtSlot(object)
    def open_expanded_view_slot(self, stream_conf: StreamConfiguration):
        """Signaled by thumbnail view when thumbnail video is clicked
        """
        if self.timer:
            self.killTimer(self.timer)

        self.expanded_video.change_stream(stream_conf)
        self.alert_log.change_stream(stream_conf.id)
        self.stream_conf = stream_conf

        # Set displayed title of stream
        self.stream_name_label.setText(stream_conf.name)

        self.timer = self.startTimer(1000)

    @pyqtSlot()
    def expanded_stream_closed_slot(self):
        """Signaled by close button"""

        self.killTimer(self.timer)
        self.timer = None

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
        print("Deleting")
        api.delete_stream_configuration(self.stream_conf.id)
        print("Done deleting")

        # Remove StreamWidgets associated with stream being deleted
        # noinspection PyUnresolvedReferences
        self.stream_delete_signal.emit(self.stream_conf)

        self.expanded_stream_closed_slot()
        self.stream_conf = None

    @pyqtSlot()
    def open_stream_plugin_config(self):
        """
        Connected to:
        - QPushButton -- QtDesigner
          self.open_stream_plugin_config.clicked
        """
        PluginConfigDialog.show_dialog(self, self.stream_conf.id)

    @pyqtSlot()
    def open_task_config(self):
        """Opens the task configuration for this stream
        Connected to:
        - QPushButton -- QtDesigner
          self.task_config_button.clicked
        """
        config = TaskConfiguration.open_configuration(self.stream_conf, self)
        if not config:
            return
