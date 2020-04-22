from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMessageBox, QWidget

from brainframe.client.api import api, api_errors
from brainframe.client.ui.main_window.activities \
    import StreamConfigurationDialog
from brainframe.client.ui.main_window.activities.stream_activity.stream_activity_ui import \
    _StreamActivityUI
from brainframe.client.ui.resources.mixins.display import ExpandableMI


class StreamActivity(_StreamActivityUI, ExpandableMI):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._init_signals()

    def _init_signals(self):
        self.video_thumbnail_view.thumbnail_stream_clicked_signal.connect(
            lambda: self.set_expanded(True))
        self.video_thumbnail_view.thumbnail_stream_clicked_signal.connect(
            self.video_expanded_view.open_expanded_view_slot)

        self.video_expanded_view.expanded_stream_closed_signal.connect(
            lambda: self.set_expanded(False))

        self.video_expanded_view.stream_delete_signal.connect(
            lambda: self.set_expanded(False))
        self.video_expanded_view.stream_delete_signal.connect(
            self.video_thumbnail_view.delete_stream_slot)

        # TODO: Move to be within video_thumbnail_view
        self.new_stream_button.clicked.connect(self.add_new_stream_slot)

    def expand(self, expanding: bool):
        self.video_expanded_view.setVisible(expanding)

        if not expanding:
            self.video_thumbnail_view.expand_thumbnail_layouts_slot()

    @pyqtSlot()
    def add_new_stream_slot(self):
        """Open dialog to add a new stream and then send it to the server"""

        stream_conf = StreamConfigurationDialog.configure_stream(self)
        if stream_conf is None:
            return
        try:
            stream_conf = api.set_stream_configuration(stream_conf)

            # Currently, we default to setting all new streams as 'active'
            api.start_analyzing(stream_conf.id)

            self.video_thumbnail_view.new_stream(stream_conf)
        except api_errors.DuplicateStreamSourceError as err:
            message_title = self.tr("Error Opening Stream")
            message_desc = self.tr("Stream source already open")
            message_info = self.tr("You already have the stream source open.")
            error_text = self.tr("Error: ")
            message = f"<b>{message_desc}</b>" \
                      f"<br><br>" \
                      f"{message_info}<br><br>" \
                      f"{error_text}<b>{err.kind}</b>"

            QMessageBox.information(self, message_title, message)
        except api_errors.StreamNotOpenedError as err:
            message_title = self.tr("Error Opening Stream")
            message_desc = self.tr("Error encountered while opening stream")
            error_text = self.tr("Error: ")
            message = f"<b>{message_desc}</b>" \
                      f"<br><br>" \
                      f"{err}<br><br>" \
                      f"{err.description}<br><br>" \
                      f"{error_text}<b>{err.kind}</b>"
            QMessageBox.information(self, message_title, message)
        except api_errors.AnalysisLimitExceededError:
            # Delete the stream configuration, since you almost never want to
            # have a stream that can't have analysis running
            api.delete_stream_configuration(stream_conf.id)

            message_title = self.tr("Error Opening Stream")
            message_desc = self.tr("Active Stream Limit Exceeded")
            message_info1 = self.tr(
                "You have exceeded the number of active streams available to "
                "you under the terms of your license. Consider deleting "
                "another stream or contacting Aotu to increase your "
                "active stream limit.")
            message = (f"<b>{message_desc}</b>"
                       f"<br><br>"
                       f"{message_info1}")
            QMessageBox.information(self, message_title, message)
        except api_errors.BaseAPIError as err:
            message_title = self.tr("Error Opening Stream")
            message_desc = self.tr("Error encountered while opening stream")
            message_info1 = self.tr("Is stream already open?")
            message_info2 = self.tr("Is this a valid stream source?")
            error_text = self.tr("Error: ")
            message = f"<b>{message_desc}</b>" \
                      f"<br><br>" \
                      f"{message_info1}<br>" \
                      f"{message_info2}<br><br>" \
                      f"{error_text}<b>{err.kind}</b>"
            QMessageBox.information(self, message_title, message)

