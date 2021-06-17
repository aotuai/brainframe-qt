import string
from pathlib import Path
from traceback import TracebackException
from typing import Callable, List, Optional, Union

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QDialogButtonBox, QWidget

from brainframe.api import bf_codecs, bf_errors

from brainframe_qt.api_utils import api, get_stream_manager
from brainframe_qt.ui.main_window.activities.stream_configuration \
    .stream_configuration_ui import StreamConfigurationUI
from brainframe_qt.ui.resources import CanceledError, ProgressFileReader, QTAsyncWorker
from brainframe_qt.ui.resources.links.documentation import IP_CAMERA_DOCS_LINK
from brainframe_qt.ui.resources.ui_elements.widgets import FileUploadProgressDialog
from brainframe_qt.ui.resources.ui_elements.widgets.dialogs import BrainFrameMessage


class StreamConfiguration(StreamConfigurationUI):
    stream_conf_deleted = pyqtSignal()
    stream_conf_modified = pyqtSignal(bf_codecs.StreamConfiguration)
    """Sent when a new or modified stream_conf has been sent to, and accepted
    by, the server"""

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._reset_stream_conf: Optional[bf_codecs.StreamConfiguration] = None
        """Holds the loaded stream configuration to revert to when Reset button
        is pressed"""

        self.validate_input()

        self._init_signals()

    def _init_signals(self) -> None:
        self.connection_type_combobox.currentIndexChanged[int].connect(
            self.connection_type_changed)

        # Validation on change
        for signal in [
            self.stream_name_line_edit.textChanged,
            self.connection_type_combobox.currentIndexChanged,
            self.stream_options.file_selector.path_changed,
            self.stream_options.webcam_device_line_edit.textChanged,
            self.stream_options.network_address_line_edit.textChanged,
            self.stream_options.advanced_options.toggled,
            self.stream_options.advanced_options.pipeline_line_edit.textChanged,
            self.stream_options.advanced_options.keyframe_only_checkbox.toggled,
        ]:
            signal.connect(self.validate_input)

        # Buttons
        self.button_box.button(QDialogButtonBox.Apply).clicked.connect(
            self._gather_and_send_stream_configuration)
        self.button_box.button(QDialogButtonBox.Reset).clicked.connect(
            self.reset_conf)
        self.stream_options.webcam_device_help_button.clicked.connect(
            self._display_webcam_help
        )
        self.stream_options.network_address_help_button.clicked.connect(
            self._display_ip_camera_help
        )

        # GroupBox
        self.stream_options.advanced_options.expansion_changed.connect(
            self._show_relevant_options)

        # TODO: Readd with a better pubsub system
        # # PubSub
        # stream_sub = zss_publisher.subscribe_streams(
        #     self._handle_stream_stream)
        # self.destroyed.connect(lambda: zss_publisher.unsubscribe(stream_sub))

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # Simulate a click on the apply button if Enter/Return is pressed while
        # the inputs are valid
        if event.key() in [Qt.Key_Enter, Qt.Key_Return]:
            if self.inputs_valid:
                apply_button = self.button_box.button(QDialogButtonBox.Apply)
                apply_button.click()
        else:
            event.ignore()

    def load_from_conf(
            self,
            stream_conf: Optional[bf_codecs.StreamConfiguration]) -> None:

        self._reset_stream_conf = stream_conf

        if stream_conf is None:
            self._load_empty_conf()
            return

        self.stream_name = stream_conf.name
        self.connection_type = stream_conf.connection_type
        self.premises = stream_conf.premises_id
        self.connection_options = stream_conf.connection_options
        self.runtime_options = stream_conf.runtime_options

        self.disable_input_fields(True)

    def _load_empty_conf(self) -> None:

        self.stream_name = ""
        self.connection_type = None
        self.premises = None
        self.connection_options = {}
        self.runtime_options = {}

        self.advanced_options_enabled = False

        self.disable_input_fields(False)

    def connection_type_changed(self, _index) -> None:

        self.stream_options.setHidden(self.connection_type is None)
        if self.connection_type is None:
            return

        self._show_relevant_options()

    def reset_conf(self) -> None:
        self.load_from_conf(self._reset_stream_conf)

    def disable_input_fields(self, disable: bool) -> None:
        self.advanced_options_enabled = disable

        self.stream_name_line_edit.setDisabled(disable)
        self.connection_type_combobox.setDisabled(disable)

        stream_options = self.stream_options
        stream_options.premises_combobox.setDisabled(disable)
        stream_options.network_address_line_edit.setDisabled(disable)
        stream_options.file_selector.setDisabled(disable)
        stream_options.webcam_device_line_edit.setDisabled(disable)

        advanced_options = stream_options.advanced_options
        advanced_options.keyframe_only_checkbox.setDisabled(disable)
        advanced_options.pipeline_line_edit.setDisabled(disable)
        advanced_options.avoid_transcoding_checkbox.setDisabled(disable)

        advanced_options.setDisabled(disable)

    def _handle_stream_stream(
            self, stream_confs: List[bf_codecs.StreamConfiguration]) \
            -> None:
        """Handles the stream of StreamConfiguration information from the
        pubsub system"""

        if self._reset_stream_conf is None:
            return

        stream_ids = [stream_conf.id for stream_conf in stream_confs]

        if self._reset_stream_conf.id not in stream_ids:
            self._reset_stream_conf = None
            self._load_empty_conf()
            self.setDisabled(True)
            self.stream_conf_deleted.emit()

    def _show_relevant_options(self) -> None:
        self.stream_options.hide_all(True)

        advanced_options = self.stream_options.advanced_options
        advanced_options_visible = advanced_options.expanded

        if self.connection_type is bf_codecs.StreamConfiguration.ConnType.IP_CAMERA:
            self.stream_options.network_address_label.setVisible(True)
            self.stream_options.network_address_line_edit.setVisible(True)
            self.stream_options.network_address_help_button.setVisible(True)
            self.stream_options.premises_label.setVisible(True)
            self.stream_options.premises_combobox.setVisible(True)
            if advanced_options_visible:
                advanced_options.keyframe_only_checkbox.setVisible(True)
        elif self.connection_type is bf_codecs.StreamConfiguration.ConnType.WEBCAM:
            self.stream_options.webcam_device_label.setVisible(True)
            self.stream_options.webcam_device_line_edit.setVisible(True)
            self.stream_options.webcam_device_help_button.setVisible(True)
        elif self.connection_type is bf_codecs.StreamConfiguration.ConnType.FILE:
            self.stream_options.filepath_label.setVisible(True)
            self.stream_options.file_selector.setVisible(True)
            if advanced_options_visible:
                advanced_options.avoid_transcoding_checkbox.setVisible(True)

        if advanced_options_visible:
            advanced_options.pipeline_label.setVisible(True)
            advanced_options.pipeline_line_edit.setVisible(True)

    def validate_input(self) -> None:
        apply_button = self.button_box.button(QDialogButtonBox.Apply)
        reset_button = self.button_box.button(QDialogButtonBox.Reset)

        apply_button.setEnabled(self.inputs_valid and self.fields_changed)
        reset_button.setEnabled(self.fields_changed)

    @property
    def inputs_valid(self) -> bool:
        if not self.stream_name:
            return False
        if self.connection_type is None:
            return False

        @property
        def pipeline_valid() -> bool:
            return not self.pipeline or "{url}" in self.pipeline

        if self.connection_type is bf_codecs.StreamConfiguration.ConnType.IP_CAMERA:
            if not self.network_address:
                return False
            if self.advanced_options_enabled:
                if not pipeline_valid:
                    return False

        elif self.connection_type is bf_codecs.StreamConfiguration.ConnType.FILE:
            if not self.filepath:
                return False
            if self.advanced_options_enabled:
                if not pipeline_valid:
                    return False

        elif self.connection_type is bf_codecs.StreamConfiguration.ConnType.WEBCAM:
            if self.webcam_device is None:
                return False

        else:
            return False

        return True

    def _gather_and_send_stream_configuration(self) -> None:
        if not self.inputs_valid:
            raise ValueError("Invalid stream configuration")

        stream_conf = bf_codecs.StreamConfiguration(
            name=self.stream_name,
            connection_type=self.connection_type,
            connection_options=self.connection_options,
            premises_id=self.premises and self.premises.id,
            runtime_options=self.runtime_options,
            metadata={}
        )

        if self.connection_type is bf_codecs.StreamConfiguration.ConnType.FILE:

            if not Path(self.filepath).is_file():
                self._handle_missing_file_error(self.filepath)
                return

            def update_and_send(storage_id: Optional[int]) -> None:
                # storage_id is None if the user canceled the upload
                if storage_id is None:
                    return

                stream_conf.connection_options["storage_id"] = storage_id
                self._send_stream_configuration(stream_conf)

            self._upload_video(callback=update_and_send)

        else:
            # No need to upload anything. Immediately send stream_conf
            self._send_stream_configuration(stream_conf)

    def _upload_video(self, *, callback: Callable) -> None:
        """Uploads a file to storage asynchronously, notifying the user of the
        upload progress using a QProgressDialog.

        :param callback: Called when the file is done uploading, providing
            the storage ID, or None if the user canceled the upload"""
        reader = ProgressFileReader(self.filepath, self)
        progress_dialog = FileUploadProgressDialog(self)

        progress_dialog.filepath = self.filepath

        reader.progress_signal.connect(progress_dialog.setValue)
        progress_dialog.canceled.connect(reader.cancel)

        def upload() -> Optional[int]:
            try:
                with reader:
                    return api.new_storage(reader, "application/octet-stream")
            except CanceledError:
                # The user canceled the upload
                return None

        def on_success(storage_id: Optional[int]):
            # Make sure the progress dialog closes
            progress_dialog.cancel()

            # storage_id is None if the user canceled the upload
            callback(storage_id)

        def on_error(exc: BaseException):
            message_title = self.tr("Error Opening Stream")
            message_desc = self.tr(
                "Error encountered while uploading video file")

            traceback_exc = TracebackException.from_exception(exc)

            BrainFrameMessage.exception(
                parent=self,
                title=message_title,
                description=message_desc,
                traceback=traceback_exc
            ).exec()

        QTAsyncWorker(self, upload, on_success=on_success, on_error=on_error) \
            .start()

    def _send_stream_configuration(
            self, stream_conf: bf_codecs.StreamConfiguration) \
            -> None:

        # Two stage QtAsyncWorker because we need to catch exceptions on both
        # api.set_stream_configuration and api.start_analyzing, but the handler
        # for exceptions in the latter needs the result of the former.

        def on_success(enabled_stream_conf: bf_codecs.StreamConfiguration):
            self.disable_input_fields(True)
            self._reset_stream_conf = enabled_stream_conf

            self.stream_conf_modified.emit(enabled_stream_conf)

        def start_analysis(sent_stream_conf: bf_codecs.StreamConfiguration):
            def on_error(exc: BaseException):
                self._handle_start_analysis_error(sent_stream_conf, exc)

            QTAsyncWorker(self, api.start_analyzing,
                          f_args=(sent_stream_conf.id,),
                          on_success=lambda _: on_success(sent_stream_conf),
                          on_error=on_error) \
                .start()

        QTAsyncWorker(self, api.set_stream_configuration,
                      f_args=(stream_conf,),
                      on_success=start_analysis,
                      on_error=self._handle_send_stream_conf_error) \
            .start()

    @property
    def advanced_options_enabled(self) -> bool:
        return self.stream_options.advanced_options.isChecked()

    @advanced_options_enabled.setter
    def advanced_options_enabled(self, advanced_options_enabled: bool) -> None:
        advanced_options = self.stream_options.advanced_options
        advanced_options.setChecked(advanced_options_enabled)

    @property
    def avoid_transcoding(self) -> Optional[bool]:
        if self.connection_type is not bf_codecs.StreamConfiguration.ConnType.FILE:
            return None
        if not self.advanced_options_enabled:
            return DefaultOptions.AVOID_TRANSCODING

        advanced_options = self.stream_options.advanced_options
        avoid_transcoding_cb = advanced_options.avoid_transcoding_checkbox
        return avoid_transcoding_cb.isChecked()

    @avoid_transcoding.setter
    def avoid_transcoding(self, avoid_transcoding: bool) -> None:
        advanced_options = self.stream_options.advanced_options
        avoid_transcoding_cb = advanced_options.avoid_transcoding_checkbox
        avoid_transcoding_cb.setChecked(avoid_transcoding)

    @property
    def connection_options(self) -> dict:
        connection_options = {}
        if self.pipeline is not None:
            connection_options["pipeline"] = self.pipeline
        if self.network_address is not None:
            connection_options["url"] = self.network_address
        if self.webcam_device is not None:
            connection_options["device_id"] = self.webcam_device
        if self.avoid_transcoding is not None:
            connection_options["transcode"] = not self.avoid_transcoding
        return connection_options

    @connection_options.setter
    def connection_options(self, connection_options: dict) -> None:
        self.pipeline = connection_options.get("pipeline")
        self.network_address = connection_options.get("url")
        self.webcam_device = connection_options.get("device_id")
        self.avoid_transcoding = connection_options.get(
            "transcode", DefaultOptions.KEYFRAME_ONLY_STREAMING)

    @property
    def connection_type(self) -> bf_codecs.StreamConfiguration.ConnType:
        return self.connection_type_combobox.currentData()

    @connection_type.setter
    def connection_type(self,
                        connection_type: bf_codecs.StreamConfiguration.ConnType) -> None:
        index = self.connection_type_combobox.findData(connection_type)
        self.connection_type_combobox.setCurrentIndex(index)

    @property
    def fields_changed(self) -> bool:
        if self._reset_stream_conf is None:
            return self._fields_changed_new_stream()

        if self.stream_name != self._reset_stream_conf.name:
            return True
        if self.connection_type is not self._reset_stream_conf.connection_type:
            return True

        premises_id = self.premises.id if self.premises is not None else None
        if premises_id != self._reset_stream_conf.premises_id:
            return True

        # Connection Options
        connection_options = self._reset_stream_conf.connection_options
        if self.pipeline != connection_options.get("pipeline"):
            return True
        if self.network_address != connection_options.get("url"):
            return True
        if self.webcam_device != connection_options.get("device_id"):
            return True

        # Runtime Options
        # Check equivalency. If either the client or server option is
        # hidden/missing, assume it is the default value
        runtime_options = self._reset_stream_conf.runtime_options
        client_keyframes_only = self.keyframe_only_streaming
        server_keyframes_only = runtime_options.get("keyframes_only", None)
        if client_keyframes_only is None:
            client_keyframes_only = DefaultOptions.KEYFRAME_ONLY_STREAMING
        if server_keyframes_only is None:
            server_keyframes_only = DefaultOptions.KEYFRAME_ONLY_STREAMING
        if server_keyframes_only != client_keyframes_only:
            return True

        # Avoid transcoding
        # Check equivalency. If either the client or server option is
        # hidden/missing, assume it is the default value
        client_avoid_transcoding = self.avoid_transcoding
        server_avoid_transcoding = runtime_options.get("transcode", None)
        if client_avoid_transcoding is None:
            client_avoid_transcoding = DefaultOptions.AVOID_TRANSCODING
        if server_avoid_transcoding is None:
            server_avoid_transcoding = DefaultOptions.AVOID_TRANSCODING
        if server_avoid_transcoding != client_avoid_transcoding:
            return True

        return False

    def _fields_changed_new_stream(self) -> bool:
        if self.stream_name != "":
            return True
        if self.connection_type is not None:
            return True
        if self.premises is not None:
            return True

        # Connection Options
        if self.connection_options != {}:
            return True
        if self.runtime_options != {}:
            return True

        return False

    @property
    def filepath(self) -> Optional[Path]:
        if self.connection_type is not bf_codecs.StreamConfiguration.ConnType.FILE:
            return None
        return self.stream_options.file_selector.filepath

    @property
    def keyframe_only_streaming(self) -> Optional[bool]:
        if self.connection_type is not bf_codecs.StreamConfiguration.ConnType.IP_CAMERA:
            return None
        if not self.advanced_options_enabled:
            return DefaultOptions.KEYFRAME_ONLY_STREAMING

        advanced_options = self.stream_options.advanced_options
        keyframe_only_checkbox = advanced_options.keyframe_only_checkbox
        return keyframe_only_checkbox.isChecked()

    @keyframe_only_streaming.setter
    def keyframe_only_streaming(self, keyframe_only_streaming: bool) -> None:
        advanced_options = self.stream_options.advanced_options
        keyframe_only_checkbox = advanced_options.keyframe_only_checkbox
        keyframe_only_checkbox.setChecked(keyframe_only_streaming)

    @property
    def network_address(self) -> Optional[str]:
        if self.connection_type is not bf_codecs.StreamConfiguration.ConnType.IP_CAMERA:
            return None

        network_address = self.stream_options.network_address_line_edit.text()
        return network_address.strip(string.whitespace)

    @network_address.setter
    def network_address(self, network_address: Optional[str]) -> None:
        network_address = "" if network_address is None else network_address
        self.stream_options.network_address_line_edit.setText(network_address)

    @property
    def pipeline(self) -> Optional[str]:
        if not self.advanced_options_enabled:
            return None

        advanced_options = self.stream_options.advanced_options
        pipeline = advanced_options.pipeline_line_edit
        return pipeline.text().strip(string.whitespace) or None

    @pipeline.setter
    def pipeline(self, pipeline: Optional[str]) -> None:
        advanced_options = self.stream_options.advanced_options
        pipeline_line_edit = advanced_options.pipeline_line_edit

        pipeline = "" if pipeline is None else pipeline
        pipeline_line_edit.setText(pipeline)

    @property
    def premises(self) -> Optional[bf_codecs.Premises]:
        if self.connection_type is not bf_codecs.StreamConfiguration.ConnType.IP_CAMERA:
            return None
        return self.stream_options.premises_combobox.currentData()

    @premises.setter
    def premises(self, premises: Optional[Union[int, bf_codecs.Premises]]) \
            -> None:

        if premises is None or isinstance(premises, bf_codecs.Premises):
            index = self.stream_options.premises_combobox.findData(premises)
            self.stream_options.premises_combobox.setCurrentIndex(index)

        elif isinstance(premises, int):
            self._set_premises_by_id(premises)

    def _set_premises_by_id(self, premises_id: int) -> None:

        def on_success(premises: bf_codecs.Premises) -> None:
            self.premises = premises

        def on_error(exc: BaseException) -> None:
            # TODO: Handle a premises that doesn't exist
            raise exc

        QTAsyncWorker(self, api.get_premises, f_args=(premises_id,),
                      on_success=on_success,
                      on_error=on_error) \
            .start()

    @property
    def runtime_options(self) -> dict:
        runtime_options = {}
        if self.keyframe_only_streaming is not None:
            runtime_options["keyframes_only"] = self.keyframe_only_streaming
        return runtime_options

    @runtime_options.setter
    def runtime_options(self, runtime_options: dict) -> None:
        self.keyframe_only_streaming = \
            runtime_options.get("keyframes_only",
                                DefaultOptions.KEYFRAME_ONLY_STREAMING)

    @property
    def stream_id(self) -> Optional[int]:
        if self._reset_stream_conf is None:
            return None

        return self._reset_stream_conf.id

    @property
    def stream_name(self) -> str:
        return self.stream_name_line_edit.text().strip(string.whitespace)

    @stream_name.setter
    def stream_name(self, stream_name: str) -> None:
        self.stream_name_line_edit.setText(stream_name)

    @property
    def webcam_device(self) -> Optional[int]:
        if self.connection_type is not bf_codecs.StreamConfiguration.ConnType.WEBCAM:
            return None

        webcam_device = self.stream_options.webcam_device_line_edit.text()
        webcam_device = webcam_device.strip(string.whitespace)

        try:
            webcam_device = int(webcam_device)
        except ValueError:
            return None

        return webcam_device

    @webcam_device.setter
    def webcam_device(self, webcam_device: Optional[int]) -> None:
        webcam_device = "" if webcam_device is None else str(webcam_device)
        self.stream_options.webcam_device_line_edit.setText(webcam_device)

    def _display_webcam_help(self):
        title = self.tr("Adding a webcam")
        message = self.tr(
            'Webcams and other video devices must be attached to the computer '
            'running the BrainFrame server.'
            '<br><br>'
            'To add a webcam, open a terminal on the server machine and run '
            '<pre>ls /dev/video*</pre>'
            'If you get a message about "No such '
            'file or directory", you do not have any webcams attached to the'
            'server computer.'
            '<br><br>'
            'Otherwise, select the digit at the end of the results and '
            'provide it to BrainFrame. For example, if the command returns '
            '"/dev/video0", input "0" (without the quotes).'
        )

        BrainFrameMessage.information(
            parent=self,
            title=title,
            message=message
        ).open()

    def _display_ip_camera_help(self):

        RTSP_FORMAT = "rtsp://[username]:[password]@[ip]:[port]"

        title = self.tr("Adding an IP Camera")
        message_desc = self.tr(
            "Standard RTSP format:<br>{rtsp_format}"
        ).format(rtsp_format=RTSP_FORMAT)
        message_docs = self.tr(
            "Please see the <a href='{ip_camera_docs_link}'>documentation</a> "
            "for more information on adding IP Cameras."
        ).format(ip_camera_docs_link=IP_CAMERA_DOCS_LINK)

        message = (
            f"{message_desc}"
            f"<br><br>"
            f"{message_docs}"
        )

        message_box = BrainFrameMessage.information(
            parent=self,
            title=title,
            message=message
        )

        message_box.setTextInteractionFlags(Qt.TextBrowserInteraction)
        message_box.open()

    def _handle_send_stream_conf_error(self, exc: BaseException) -> None:

        message_title = self.tr("Error Opening Stream")

        if isinstance(exc, bf_errors.DuplicateStreamSourceError):
            message_desc = self.tr("Stream source already open")
            message_info = self.tr("You already have the stream source open.")
            error_text = self.tr("Error: ")
            message = f"<b>{message_desc}</b>" \
                      f"<br><br>" \
                      f"{message_info}<br><br>" \
                      f"{error_text}<b>{exc.kind}</b>"

        elif isinstance(exc, bf_errors.StreamNotOpenedError):
            message_desc = self.tr("Error encountered while opening stream")
            error_text = self.tr("Error: ")
            message = f"<b>{message_desc}</b>" \
                      f"<br><br>" \
                      f"{exc}<br><br>" \
                      f"{exc.description}<br><br>" \
                      f"{error_text}<b>{exc.kind}</b>"

        elif isinstance(exc, bf_errors.BaseAPIError):
            message_desc = self.tr("Error encountered while opening stream")
            message_info1 = self.tr("Is stream already open?")
            message_info2 = self.tr("Is this a valid stream source?")
            error_text = self.tr("Error: ")
            message = f"<b>{message_desc}</b>" \
                      f"<br><br>" \
                      f"{message_info1}<br>" \
                      f"{message_info2}<br><br>" \
                      f"{error_text}<b>{exc.kind}</b>"

        else:
            raise exc

        BrainFrameMessage.information(
            parent=self,
            title=message_title,
            message=message
        ).open()

    def _handle_start_analysis_error(
            self, stream_conf: bf_codecs.StreamConfiguration,
            exc: BaseException) \
            -> None:
        if isinstance(exc, bf_errors.AnalysisLimitExceededError):
            # Delete the stream configuration, since you almost never want to
            # have a stream that can't have analysis running
            QTAsyncWorker(self, get_stream_manager().delete_stream,
                          f_args=(stream_conf.id,)) \
                .start()

            message_title = self.tr("Active Stream Limit Exceeded")
            message_desc = self.tr(
                "You have exceeded the number of active streams available to "
                "you under the terms of your license. Consider deleting "
                "another stream or contacting Aotu to increase your "
                "active stream limit.")

            BrainFrameMessage.warning(
                parent=self,
                title=message_title,
                warning=message_desc).exec()

        else:
            raise exc

    def _handle_missing_file_error(self, filepath: Path) -> None:
        message_title = self.tr("Error uploading file")
        message_info = self.tr("No such file: {filepath}") \
            .format(filepath=filepath)

        BrainFrameMessage.warning(
            parent=self,
            title=message_title,
            warning=message_info
        ).open()


class DefaultOptions:
    AVOID_TRANSCODING: bool = False
    KEYFRAME_ONLY_STREAMING: bool = False
