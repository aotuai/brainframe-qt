import logging
import typing

from PyQt5.QtCore import QEvent, QTimerEvent, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from brainframe.api.bf_codecs import StreamConfiguration
from requests.exceptions import RequestException

from brainframe_qt.api_utils import api, get_stream_manager
from brainframe_qt.ui.dialogs import CapsuleConfigDialog, TaskConfiguration
from brainframe_qt.ui.resources import QTAsyncWorker, stylesheet_watcher
from brainframe_qt.ui.resources.paths import qt_qss_paths, qt_ui_paths
from brainframe_qt.ui.resources.ui_elements.buttons import FloatingXButton
from brainframe_qt.ui.resources.ui_elements.widgets.dialogs import BrainFrameMessage


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

    stream_delete_signal = pyqtSignal(StreamConfiguration)
    """Called when the user wants to delete a stream"""

    toggle_stream_config_signal = pyqtSignal(StreamConfiguration)
    """Called when the user clicks the Stream Config button"""

    def __init__(self, parent):
        super().__init__(parent)

        loadUi(qt_ui_paths.video_expanded_view_ui, self)

        self.hide_button: FloatingXButton = None

        self.stream_conf = typing.cast(StreamConfiguration, None)

        self._init_ui()
        self._init_signals()

        self.startTimer(1000)

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

        stylesheet_watcher.watch(self, qt_qss_paths.video_expanded_view_qss)

    def _init_signals(self):
        self.stream_config_button.clicked.connect(
            lambda: self.toggle_stream_config_signal.emit(self.stream_conf))

    def enterEvent(self, event: QEvent):
        self.hide_button.show()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent):
        self.hide_button.hide()
        super().leaveEvent(event)

    def timerEvent(self, timer_event: QTimerEvent):
        """Close the expanded view if the currently open stream no longer
        exists on the server"""
        # Don't do anything if we don't have an active stream_conf
        if not self.stream_conf:
            return

        def get_stream_configurations():
            try:
                stream_configurations = api.get_stream_configurations()
                return stream_configurations
            except RequestException as ex:
                logging.error(f"Error while polling for stream "
                              f"configurations: {ex}")
                return None

        def check_deleted(stream_configurations):
            if stream_configurations is None:
                # An error occurred while fetching stream configurations
                return

            if self.stream_conf:
                for stream_conf in stream_configurations:
                    if self.stream_conf.id == stream_conf.id:
                        return
            self.expanded_stream_closed_slot()

        QTAsyncWorker(self, get_stream_configurations,
                      on_success=check_deleted) \
            .start()

    @pyqtSlot(object)
    def open_expanded_view_slot(self, stream_conf: StreamConfiguration):
        """Signaled by thumbnail view when thumbnail video is clicked
        """
        self.expanded_video.change_stream(stream_conf)
        self.alert_log.change_stream(stream_conf.id)
        self.stream_conf = stream_conf

    @pyqtSlot()
    def expanded_stream_closed_slot(self):
        """Signaled by close button"""

        # Stop attempting to display a stream
        self.expanded_video.stop_streaming()

        # Stop alert log from asking for alerts from stream
        self.alert_log.stop_streaming()

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

        if not self._confirm_stream_delete():
            return

        # Delete stream from database
        QTAsyncWorker(
            self, get_stream_manager().delete_stream,
            f_args=(self.stream_conf.id, 600)
        ).start()

        # Remove StreamWidgets associated with stream being deleted
        self.stream_delete_signal.emit(self.stream_conf)

        self.expanded_stream_closed_slot()

    @pyqtSlot()
    def open_stream_capsule_config(self):
        """
        Connected to:
        - QPushButton -- QtDesigner
          self.open_stream_capsule_config.clicked
        """
        CapsuleConfigDialog.show_dialog(self, self.stream_conf.id)

    @pyqtSlot()
    def open_task_config(self):
        """Opens the task configuration for this stream
        Connected to:
        - QPushButton -- QtDesigner
          self.task_config_button.clicked
        """
        TaskConfiguration.open_configuration(self.stream_conf, self)

    def _confirm_stream_delete(self) -> bool:
        title = self.tr("Delete stream?")

        question = self.tr(
            'Deleting stream "{stream_name}".'
        ).format(stream_name=self.stream_conf.name)

        subtext = self.tr(
            "This will delete all Zones, Detections, Alarms, Alerts, etc. "
            "associated with this stream and cannot be undone. This process "
            "will happen in the background and can take several minutes."
            "<br><br>"
            "Are you sure you want to continue?"
        )

        result = BrainFrameMessage.question(
            parent=self,
            title=title,
            question=question,
            subtext=subtext
        ).exec()

        return result == BrainFrameMessage.Yes
