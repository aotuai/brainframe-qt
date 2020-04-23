from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import QWidget

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

    def connection_type_changed(self, index):
        connection_type: Optional[self.ConnType] \
            = self.connection_type_combobox.itemData(index)

        if connection_type is None:
            self.stream_options.setHidden(True)
            return
        if connection_type is ConnType.IP_CAMERA:
            print("IP Camera")
        if connection_type is ConnType.WEBCAM:
            print("Webcam")
        if connection_type is ConnType.FILE:
            print("File")

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
        return self.filepath_selector.filepath

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
