from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import QDialogButtonBox, QWidget

from brainframe.client.ui.main_window.activities.stream_configuration \
    .stream_configuration_ui import StreamConfigurationUI
from brainframe.shared.codec_enums import ConnType


class StreamConfiguration(StreamConfigurationUI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

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

    @property
    def advanced_options_enabled(self) -> bool:
        return self.stream_options.advanced_options.isChecked()

    @property
    def avoid_transcoding(self) -> bool:
        advanced_options = self.stream_options.advanced_options
        avoid_transcoding = advanced_options.avoid_transcoding_checkbox
        return avoid_transcoding.isChecked()

    @property
    def connection_type(self) -> ConnType:
        return self.connection_type_combobox.currentData()

    @property
    def filepath(self) -> Path:
        return self.stream_options.file_selector.filepath

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

    @property
    def keyframe_only_streaming(self) -> bool:
        advanced_options = self.stream_options.advanced_options
        keyframe_only_checkbox = advanced_options.keyframe_only_checkbox
        return keyframe_only_checkbox.isChecked()

    @property
    def pipeline(self) -> str:
        advanced_options = self.stream_options.advanced_options
        pipeline = advanced_options.pipeline_line_edit
        return pipeline.text()

    @property
    def premises(self):
        return self.stream_options.premises_combobox

    @property
    def stream_name(self) -> str:
        return self.stream_name_label.text()

    @property
    def webcam_device(self) -> str:
        return self.stream_options.webcam_device_line_edit.text()
