from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QComboBox, QDialogButtonBox, \
    QGridLayout, QGroupBox, \
    QLabel, QLineEdit, QSizePolicy, QWidget
from brainframe.api.bf_codecs import Premises, StreamConfiguration

from brainframe.client.api_utils import api
from brainframe.client.ui.resources import QTAsyncWorker, stylesheet_watcher
from brainframe.client.ui.resources.mixins.display import ExpandableMI
from brainframe.client.ui.resources.paths import qt_qss_paths
from brainframe.client.ui.resources.ui_elements.buttons import TextIconButton
from brainframe.client.ui.resources.ui_elements.widgets import FileSelector, \
    Line


class StreamConfigurationUI(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.stream_name_label = self._init_stream_name_label()
        self.stream_name_line_edit = self._init_stream_name_line_edit()

        self.connection_type_label = self._init_connection_type_label()
        self.connection_type_combobox = self._init_connection_type_combobox()

        self.stream_options = self._init_stream_options_gb()

        self.button_box = self._init_button_box()

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
        connection_type_combobox.addItem(
            ip_camera_text, StreamConfiguration.ConnType.IP_CAMERA)
        connection_type_combobox.addItem(
            webcam_text, StreamConfiguration.ConnType.WEBCAM)
        connection_type_combobox.addItem(
            video_file_text, StreamConfiguration.ConnType.FILE)

        return connection_type_combobox

    def _init_stream_options_gb(self) -> "_StreamOptions":
        title = self.tr("Stream Options")
        stream_options = _StreamOptions(title, self)
        stream_options.setObjectName("stream_options")

        stream_options.setFlat(True)
        stream_options.setSizePolicy(QSizePolicy.Preferred,
                                     QSizePolicy.Maximum)

        return stream_options

    def _init_button_box(self) -> QDialogButtonBox:
        button_box = QDialogButtonBox(self)

        button_box.setStandardButtons(QDialogButtonBox.Reset |
                                      QDialogButtonBox.Apply)

        return button_box

    def _init_layout(self) -> None:
        layout = QGridLayout()

        layout.addWidget(self.stream_name_label, 0, 0)
        layout.addWidget(self.stream_name_line_edit, 0, 1)
        layout.addWidget(self.connection_type_label, 1, 0)
        layout.addWidget(self.connection_type_combobox, 1, 1)
        layout.addWidget(Line.h_line(self), 2, 0, 1, 2)
        layout.addWidget(self.stream_options, 3, 0, 1, 2)

        layout.addWidget(self.button_box, 4, 0, 1, 2)

        self.stream_options.setHidden(True)

        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)

    def _init_style(self) -> None:
        # Allow background of widget to be styled
        self.setAttribute(Qt.WA_StyledBackground, True)

        stylesheet_watcher.watch(self, qt_qss_paths.stream_configuration_qss)


class _StreamOptions(QGroupBox):

    def __init__(self, title: str, parent: QWidget):
        super().__init__(title, parent)

        self.network_address_label = self._init_network_address_label()
        self.network_address_line_edit = self._init_network_address_line_edit()
        self.network_address_help_button \
            = self._init_network_address_help_button()

        self.webcam_device_label = self._init_webcam_device_label()
        self.webcam_device_line_edit = self._init_webcam_device_line_edit()
        self.webcam_device_help_button = self._init_webcam_device_help_button()

        self.filepath_label = self._init_filepath_label()
        self.file_selector = self._init_file_selector()

        self.premises_label = self._init_premises_label()
        self.premises_combobox = self._init_premises_combobox()

        self.advanced_options = self._init_advanced_options_gb()

        self._init_layout()

    def _init_network_address_label(self) -> QLabel:
        text = self.tr("Network address")
        network_address_label = QLabel(text, self)

        return network_address_label

    def _init_network_address_line_edit(self) -> QLineEdit:
        network_address_line_edit = QLineEdit(self)
        return network_address_line_edit

    def _init_network_address_help_button(self) -> TextIconButton:
        network_address_help_button = TextIconButton("?️", self)
        network_address_help_button.setObjectName("help_button")

        network_address_help_button.setFlat(True)

        return network_address_help_button

    def _init_webcam_device_label(self) -> QLabel:
        text = self.tr("Device ID")
        webcam_device_label = QLabel(text, self)

        return webcam_device_label

    def _init_webcam_device_line_edit(self) -> QLineEdit:
        webcam_device_line_edit = QLineEdit(self)
        return webcam_device_line_edit

    def _init_webcam_device_help_button(self) -> TextIconButton:
        webcam_device_help_button = TextIconButton("?️", self)
        webcam_device_help_button.setObjectName("help_button")

        webcam_device_help_button.setFlat(True)

        return webcam_device_help_button

    def _init_filepath_label(self) -> QLabel:
        text = self.tr("Filepath")
        file_path_label = QLabel(text, self)

        return file_path_label

    def _init_file_selector(self) -> FileSelector:
        file_selector = FileSelector(self)
        return file_selector

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
        advanced_options = _AdvancedOptionsGroupBox(self)
        advanced_options.setTitle(self.tr("Advanced Options"))
        advanced_options.setObjectName("advanced_options")

        advanced_options.setCheckable(True)
        advanced_options.setSizePolicy(QSizePolicy.Preferred,
                                       QSizePolicy.Maximum)

        return advanced_options

    def _init_layout(self):
        layout = QGridLayout()

        layout.addWidget(self.network_address_label, 0, 0)
        layout.addWidget(self.network_address_line_edit, 0, 1)
        layout.addWidget(self.network_address_help_button, 0, 2)

        layout.addWidget(self.webcam_device_label, 2, 0)
        layout.addWidget(self.webcam_device_line_edit, 2, 1)
        layout.addWidget(self.webcam_device_help_button, 2, 2)

        layout.addWidget(self.filepath_label, 3, 0)
        layout.addWidget(self.file_selector, 3, 1, 1, 2)

        layout.addWidget(self.premises_label, 4, 0)
        layout.addWidget(self.premises_combobox, 4, 1, 1, 2)

        layout.addWidget(Line.h_line(self), 5, 0, 1, 3)

        layout.addWidget(self.advanced_options, 6, 0, 1, 3)

        self.setLayout(layout)

    def hide_all(self, hidden: bool) -> None:
        self.network_address_label.setHidden(hidden)
        self.network_address_line_edit.setHidden(hidden)
        self.network_address_help_button.setHidden(hidden)
        self.webcam_device_label.setHidden(hidden)
        self.webcam_device_line_edit.setHidden(hidden)
        self.webcam_device_help_button.setHidden(hidden)
        self.filepath_label.setHidden(hidden)
        self.file_selector.setHidden(hidden)
        self.premises_label.setHidden(hidden)
        self.premises_combobox.setHidden(hidden)

        self.advanced_options.hide_all(hidden)


class _AdvancedOptionsGroupBox(QGroupBox, ExpandableMI):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.pipeline_label = self._init_pipeline_label()
        self.pipeline_line_edit = self._init_pipeline_line_edit()

        self.avoid_transcoding_checkbox \
            = self._init_avoid_transcoding_checkbox()
        self.keyframe_only_checkbox \
            = self._init_keyframe_only_checkbox()

        self._init_layout()
        self._init_signals()

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
        layout.addWidget(self.keyframe_only_checkbox, 2, 0, 1, 2)

        self.setLayout(layout)

    def expand(self, expanding: bool) -> None:
        self.hide_all(not expanding)

    def hide_all(self, hidden: bool) -> None:
        self.pipeline_label.setHidden(hidden)
        self.pipeline_line_edit.setHidden(hidden)
        self.avoid_transcoding_checkbox.setHidden(hidden)
        self.keyframe_only_checkbox.setHidden(hidden)

    def _init_signals(self) -> None:
        self.toggled.connect(self.set_expanded)
