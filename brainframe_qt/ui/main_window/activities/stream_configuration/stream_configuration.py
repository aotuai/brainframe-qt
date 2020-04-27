from pathlib import Path
from typing import Callable, Optional

from PyQt5.QtWidgets import QDialogButtonBox, QMessageBox, QWidget

from brainframe.client.api import api, api_errors, codecs
from brainframe.client.ui.main_window.activities.stream_configuration \
    .stream_configuration_ui import StreamConfigurationUI
from brainframe.client.ui.resources import CanceledError, ProgressFileReader, \
    QTAsyncWorker
from brainframe.client.ui.resources.ui_elements.widgets import \
    FileUploadProgressDialog
from brainframe.shared.codec_enums import ConnType


class StreamConfiguration(StreamConfigurationUI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

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
        ]:
            signal.connect(self.validate_input)

        self.button_box.button(QDialogButtonBox.Apply).clicked.connect(
            self._gather_and_send_stream_configuration
        )

    def connection_type_changed(self, index):
        connection_type: Optional[ConnType] \
            = self.connection_type_combobox.itemData(index)

        self.stream_options.setHidden(connection_type is None)
        if connection_type is None:
            return

        self.stream_options.hide_all(True)

        if connection_type is ConnType.IP_CAMERA:
            self.stream_options.network_address_label.setVisible(True)
            self.stream_options.network_address_line_edit.setVisible(True)
            self.stream_options.advanced_options \
                .keyframe_only_streaming_checkbox.setVisible(True)
            self.stream_options.premises_label.setVisible(True)
            self.stream_options.premises_combobox.setVisible(True)
        elif connection_type is ConnType.WEBCAM:
            self.stream_options.webcam_device_label.setVisible(True)
            self.stream_options.webcam_device_line_edit.setVisible(True)
        elif connection_type is ConnType.FILE:
            self.stream_options.filepath_label.setVisible(True)
            self.stream_options.file_selector.setVisible(True)
            self.stream_options.advanced_options.avoid_transcoding_checkbox \
                .setVisible(True)

        self.stream_options.advanced_options.pipeline_label.setVisible(True)
        self.stream_options.advanced_options.pipeline_line_edit \
            .setVisible(True)

    def validate_input(self) -> None:
        apply_button = self.button_box.button(QDialogButtonBox.Apply)
        apply_button.setEnabled(self.inputs_valid)

    @property
    def inputs_valid(self) -> bool:
        if not self.stream_name:
            return False
        if self.connection_type is None:
            return False

        @property
        def pipeline_valid() -> bool:
            return not self.pipeline or "{url}" in self.pipeline

        if self.connection_type is ConnType.IP_CAMERA:
            if not self.network_address:
                return False
            if self.advanced_options_enabled:
                if not pipeline_valid:
                    return False

        elif self.connection_type is ConnType.FILE:
            if not self.filepath:
                return False
            if self.advanced_options_enabled:
                if not pipeline_valid:
                    return False

        elif self.connection_type is ConnType.WEBCAM:
            if not self.webcam_device:
                return False

        else:
            return False

        return True

    def _gather_and_send_stream_configuration(self):
        if not self.inputs_valid:
            raise ValueError("Invalid stream configuration")

        stream_conf = codecs.StreamConfiguration(
            name=self.stream_name,
            connection_type=self.connection_type,
            connection_options={
                "pipeline": self.pipeline,
                "url": self.network_address,
                "device_id": self.webcam_device
            },
            premises_id=self.premises and self.premises.id,
            runtime_options={
                "keyframes_only": self.keyframe_only_streaming
            },
            metadata={}
        )

        if self.connection_type is ConnType.FILE:
            def update_and_send(storage_id: Optional[int]):
                # storage_id is None if the user canceled the upload
                if storage_id is None:
                    return

                stream_conf.connection_options["storage_id"] = storage_id
                self._send_stream_configuration(stream_conf)

            self._upload_video(callback=update_and_send)

        else:
            # No need to upload anything. Immediately send stream_conf
            self._send_stream_configuration(stream_conf)

    def _upload_video(self, *, callback: Callable):
        """Uploads a file to storage asynchronously, notifying the user of the
        upload progress using a QProgressDialog.

        :param callback: Called when the file is done uploading, providing
            the storage ID, or None if the user canceled the upload"""
        reader = ProgressFileReader(self.filepath, self)
        progress_dialog = FileUploadProgressDialog(self)

        progress_dialog.filepath = self.filepath

        reader.progress_signal.connect(progress_dialog.setValue)
        progress_dialog.canceled.connect(reader.cancel)

        def upload():
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
            message = (f"<b>{message_desc}</b>"
                       f"<br><br>"
                       f"{exc}")
            QMessageBox.information(self, message_title, message)

        QTAsyncWorker(self, upload, on_success=on_success, on_error=on_error) \
            .start()

    def _send_stream_configuration(
            self, stream_conf: codecs.StreamConfiguration) \
            -> None:

        # Two stage QtAsyncWorker because we need to catch exceptions on both
        # api.set_stream_configuration and api.start_analyzing, but the handler
        # for exceptions in the latter needs the result of the former.

        def on_success(_enabled_stream_conf: codecs.StreamConfiguration):
            self.setDisabled(True)

        def start_analysis(sent_stream_conf: codecs.StreamConfiguration):

            def on_error(exc: BaseException):
                self._handle_start_analysis_error(sent_stream_conf, exc)

            QTAsyncWorker(self, api.start_analyzing,
                          f_args=(sent_stream_conf.id, ),
                          on_success=on_success,
                          on_error=on_error)

        QTAsyncWorker(self, api.set_stream_configuration,
                      f_args=(stream_conf, ),
                      on_success=start_analysis,
                      on_error=self._handle_send_stream_conf_error) \
            .start()

    @property
    def advanced_options_enabled(self) -> bool:
        return self.stream_options.advanced_options.isChecked()

    @property
    def avoid_transcoding(self) -> Optional[bool]:
        if self.connection_type is not ConnType.FILE:
            return None
        if not self.advanced_options_enabled:
            return None

        advanced_options = self.stream_options.advanced_options
        avoid_transcoding = advanced_options.avoid_transcoding_checkbox
        return avoid_transcoding.isChecked()

    @property
    def connection_type(self) -> ConnType:
        return self.connection_type_combobox.currentData()

    @property
    def filepath(self) -> Optional[Path]:
        if self.connection_type is not ConnType.FILE:
            return None
        return self.stream_options.file_selector.filepath

    @property
    def keyframe_only_streaming(self) -> Optional[bool]:
        if self.connection_type is not ConnType.IP_CAMERA:
            return None
        if not self.advanced_options_enabled:
            return None

        advanced_options = self.stream_options.advanced_options
        keyframe_only_checkbox = advanced_options.keyframe_only_checkbox
        return keyframe_only_checkbox.isChecked()

    @property
    def network_address(self) -> Optional[str]:
        if self.connection_type is not ConnType.IP_CAMERA:
            return None

        return self.stream_options.network_address_line_edit.text()

    @property
    def pipeline(self) -> Optional[str]:
        if not self.advanced_options_enabled:
            return None

        advanced_options = self.stream_options.advanced_options
        pipeline = advanced_options.pipeline_line_edit
        return pipeline.text() or None

    @property
    def premises(self) -> Optional[codecs.Premises]:
        if self.connection_type is not ConnType.IP_CAMERA:
            return None
        return self.stream_options.premises_combobox

    @property
    def stream_name(self) -> str:
        return self.stream_name_label.text()

    @property
    def webcam_device(self) -> Optional[str]:
        if self.connection_type is not ConnType.WEBCAM:
            return None
        return self.stream_options.webcam_device_line_edit.text()

    def _handle_send_stream_conf_error(self, exc: BaseException) -> None:

        message_title = self.tr("Error Opening Stream")

        if exc is api_errors.DuplicateStreamSourceError:
            message_desc = self.tr("Stream source already open")
            message_info = self.tr("You already have the stream source open.")
            error_text = self.tr("Error: ")
            message = f"<b>{message_desc}</b>" \
                      f"<br><br>" \
                      f"{message_info}<br><br>" \
                      f"{error_text}<b>{exc.kind}</b>"

        elif exc is api_errors.StreamNotOpenedError:
            message_desc = self.tr("Error encountered while opening stream")
            error_text = self.tr("Error: ")
            message = f"<b>{message_desc}</b>" \
                      f"<br><br>" \
                      f"{exc}<br><br>" \
                      f"{exc.description}<br><br>" \
                      f"{error_text}<b>{exc.kind}</b>"

        elif exc is api_errors.BaseAPIError:
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

        QMessageBox.information(self, message_title, message)

    def _handle_start_analysis_error(
            self, stream_conf: codecs.StreamConfiguration,
            exc: BaseException) \
            -> None:
        if exc is api_errors.AnalysisLimitExceededError:
            # Delete the stream configuration, since you almost never want to
            # have a stream that can't have analysis running
            QTAsyncWorker(self, api.delete_stream_configuration,
                          f_args=(stream_conf.id, )) \
                .start()

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

        else:
            raise exc
