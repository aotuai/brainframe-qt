from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QComboBox, QGridLayout, QGroupBox, \
    QLabel, \
    QLineEdit, QSizePolicy, QWidget

from brainframe.client.api import api
from brainframe.client.api.codecs import Premises
from brainframe.client.ui.resources import QTAsyncWorker, stylesheet_watcher
from brainframe.client.ui.resources.paths import qt_qss_paths
from brainframe.shared.codec_enums import ConnType


class StreamConfigurationUI(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.stream_name_label = self._init_stream_name_label()
        self.stream_name_line_edit = self._init_stream_name_line_edit()

        self.connection_type_label = self._init_connection_type_label()
        self.connection_type_combobox = self._init_connection_type_combobox()

        self.stream_options = self._init_stream_options_gb()

        self._init_layout()
        self._init_style()

    def _init_stream_name_label(self) -> QLabel:
        stream_name_label = QLabel(self.tr("Stream Name"), self)

        return stream_name_label

    def _init_stream_name_line_edit(self) -> QLineEdit:
        stream_name_line_edit = QLineEdit(self)

        stream_name_line_edit.setPlaceholderText(self.tr("Stream Name"))

        return stream_name_line_edit

    def _init_connection_type_label(self) -> QLabel:
        text = self.tr("Connection Type")
        connection_type_label = QLabel(text, self)

        return connection_type_label

    def _init_connection_type_combobox(self) -> QComboBox:
        connection_type_combobox = QComboBox(self)

        ip_camera_text = self.tr("IP Camera")
        webcam_text = self.tr("Webcam")
        video_file_text = self.tr("Video File")

        connection_type_combobox.addItem("", None)
        connection_type_combobox.addItem(ip_camera_text, ConnType.IP_CAMERA)
        connection_type_combobox.addItem(webcam_text, ConnType.WEBCAM)
        connection_type_combobox.addItem(video_file_text, ConnType.FILE)

        return connection_type_combobox

    def _init_stream_options_gb(self) -> "_StreamOptions":
        title = self.tr("Stream Options")
        stream_options = _StreamOptions(title, self)
        stream_options.setObjectName("stream_options")

        stream_options.setFlat(True)
        stream_options.setSizePolicy(QSizePolicy.Preferred,
                                     QSizePolicy.Maximum)

        return stream_options

    def _init_layout(self) -> None:
        layout = QGridLayout()

        layout.addWidget(self.stream_name_label, 0, 0)
        layout.addWidget(self.stream_name_line_edit, 0, 1)
        layout.addWidget(self.connection_type_label, 1, 0)
        layout.addWidget(self.connection_type_combobox, 1, 1)
        layout.addWidget(self.stream_options, 2, 0, 1, 2)

        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.stream_configuration_qss)


class _StreamOptions(QGroupBox):

    def __init__(self, title: str, parent: QWidget):
        super().__init__(title, parent)

        self.filepath_label = self._init_filepath_label()
        self.file_selector = self._init_file_selector()

        self.premises_label = self._init_premises_label()
        self.premises_combobox = self._init_premises_combobox()

        self.advanced_options = self._init_advanced_options_gb()

        self._init_layout()

    def _init_filepath_label(self) -> QLabel:
        text = self.tr("Filepath")
        file_path_label = QLabel(text, self)

        return file_path_label

    def _init_file_selector(self) -> QWidget:
        # TODO: Create a resource
        ...
        return QWidget(self)

    def _init_premises_label(self) -> QLabel:
        text = self.tr("Premises")
        premises_label = QLabel(text, self)
        return premises_label

    def _init_premises_combobox(self) -> QComboBox:
        premises_combobox = QComboBox(self)
        premises_combobox.addItem(self.tr("Local Network"), None)

        def handle_premises(all_premises: List[Premises]):
            for premises in all_premises:
                premises_combobox.addItem(premises.name, premises)

        def handle_error(exc: BaseException):
            # TODO: Inform user
            raise exc

        QTAsyncWorker(self, api.get_all_premises,
                      on_success=handle_premises,
                      on_error=handle_error)

        return premises_combobox

    def _init_advanced_options_gb(self) -> "_AdvancedOptionsGroupBox":
        title = self.tr("Advanced Options")
        advanced_options = _AdvancedOptionsGroupBox(title, self)
        advanced_options.setObjectName("advanced_options")

        advanced_options.setCheckable(True)
        advanced_options.setSizePolicy(QSizePolicy.Preferred,
                                       QSizePolicy.Maximum)

        return advanced_options

    def _init_layout(self):
        layout = QGridLayout()

        layout.addWidget(self.filepath_label, 0, 0)
        layout.addWidget(self.file_selector, 0, 1)

        layout.addWidget(self.premises_label, 1, 0)
        layout.addWidget(self.premises_combobox, 1, 1)

        layout.addWidget(self.advanced_options, 2, 0, 1, 2)

        self.setLayout(layout)


class _AdvancedOptionsGroupBox(QGroupBox):

    def __init__(self, title: str, parent: QWidget):
        super().__init__(title, parent)

        self.pipeline_label = self._init_pipeline_label()
        self.pipeline_line_edit = self._init_pipeline_line_edit()

        self.avoid_transcoding_checkbox \
            = self._init_avoid_transcoding_checkbox()
        self.keyframe_only_streaming_checkbox \
            = self._init_keyframe_only_checkbox()

        self._init_layout()

    def _init_pipeline_label(self) -> QLabel:
        text = self.tr("Pipeline")
        label = QLabel(text, self)
        return label

    def _init_pipeline_line_edit(self) -> QLineEdit:
        pipeline_line_edit = QLineEdit(self)

        pipeline_line_edit.setPlaceholderText(self.tr("None"))

        return pipeline_line_edit

    def _init_avoid_transcoding_checkbox(self) -> QCheckBox:
        text = self.tr("Avoid transcoding")
        avoid_transcoding_checkbox = QCheckBox(text, self)

        return avoid_transcoding_checkbox

    def _init_keyframe_only_checkbox(self) -> QCheckBox:
        text = self.tr("Keyframe-only streaming")
        keyframe_only_checkbox = QCheckBox(text, self)

        return keyframe_only_checkbox

    def _init_layout(self) -> None:
        layout = QGridLayout()

        layout.addWidget(self.pipeline_label, 0, 0)
        layout.addWidget(self.pipeline_line_edit, 0, 1)
        layout.addWidget(self.avoid_transcoding_checkbox, 1, 0, 1, 2)
        layout.addWidget(self.keyframe_only_streaming_checkbox, 2, 0, 1, 2)

        self.setLayout(layout)
