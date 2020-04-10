from pathlib import Path
from typing import Optional, Callable

from PyQt5.QtCore import Qt, pyqtSlot, QStandardPaths, QObject
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog,
    QDialogButtonBox,
    QComboBox,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QProgressDialog,
)
from PyQt5.uic import loadUi

from brainframe.client.ui.resources.paths import image_paths, qt_ui_paths
from brainframe.client.ui.resources import (
    ProgressFileReader,
    CanceledError,
    QTAsyncWorker,
)
from brainframe.client.api import api
from brainframe.client.api.codecs import StreamConfiguration


class StreamConfigurationDialog(QDialog):
    """Dialog for configuring a Stream"""
    parameter_value: QLineEdit
    pipeline_value: QLineEdit
    pipeline_value: QLineEdit
    stream_name: QLineEdit
    advanced_options_checkbox: QCheckBox
    connection_type_combo_box: QComboBox
    premises_combobox: QComboBox
    keyframe_only_checkbox: QCheckBox
    avoid_transcoding_checkbox: QCheckBox
    select_file_button: QPushButton

    def __init__(self, parent=None, stream_conf=None):
        super().__init__(parent)

        loadUi(qt_ui_paths.stream_configuration_ui, self)

        if stream_conf:
            pass
        else:
            self.connection_type = None

        if self.connection_type is None:
            self._set_parameter_widgets_hidden(True)

        # Set the alert icon on the left of the log entry
        self.select_file_button.setText("")
        pixmap = QPixmap(str(image_paths.folder_icon))
        pixmap = pixmap.scaled(32, 32, transformMode=Qt.SmoothTransformation)
        self.select_file_button.setIcon(QIcon(pixmap))

        self.select_file_button.clicked.connect(self._file_dialog)

        self.stream_name.textChanged.connect(self.verify_inputs_valid)
        self.connection_type_combo_box.currentTextChanged.connect(
            self.verify_inputs_valid)
        self.parameter_value.textChanged.connect(
            self.verify_inputs_valid)
        self.pipeline_value.textChanged.connect(
            self.verify_inputs_valid)
        self.advanced_options_checkbox.stateChanged.connect(
            self.verify_inputs_valid)
        self.avoid_transcoding_checkbox.stateChanged.connect(
            self.verify_inputs_valid)
        self.verify_inputs_valid()

        self.advanced_options_checkbox.stateChanged.connect(
            self.update_advanced_option_items)

        # Start with advanced options hidden
        self.update_advanced_option_items()

    @classmethod
    def configure_stream(cls,
                         on_success: Callable[[StreamConfiguration], None],
                         on_error: Callable[[Exception], None],
                         parent: QObject,
                         stream_conf=None) -> None:
        """Asynchronously creates a new stream configuration dialog and
        converts the results to a stream configuration.

        :param on_success: Called when the stream configuration is created
        :param on_error: Called if there was an error while creating the config
        :param parent: A parent UI object to make the dialog a child to
        :param stream_conf: If provided, fields in the dialog will be
            pre-filled with the values in this object. (Not currently
            implemented)
        """
        dialog = cls(parent, stream_conf)
        result = dialog.exec_()
        if not result:
            # The user cancelled out of the dialog, do nothing
            return None

        params = {}

        # Add the pipeline value if it was configured
        pipeline = dialog.pipeline_value.text()
        if dialog.advanced_options_checkbox.isChecked() and pipeline:
            params["pipeline"] = pipeline

        keyframes_only = False

        premises_id = None
        if dialog.connection_type == StreamConfiguration.ConnType.IP_CAMERA:
            url = dialog.parameter_value.text().strip()
            params["url"] = url

            premises_id = dialog.premises_combobox.itemData(
                dialog.premises_combobox.currentIndex())
            keyframes_only = \
                dialog.advanced_options_checkbox.isChecked() \
                and dialog.keyframe_only_checkbox.isChecked()
        elif dialog.connection_type == StreamConfiguration.ConnType.WEBCAM:
            device_id = dialog.parameter_value.text().strip()
            params["device_id"] = device_id
        elif dialog.connection_type == StreamConfiguration.ConnType.FILE:
            params["transcode"] = \
                not (dialog.advanced_options_checkbox.isChecked()
                     and dialog.avoid_transcoding_checkbox.isChecked())
            # The storage_id field will be filled in later
        else:
            message = QApplication.translate('StreamConfigurationDialog',
                                             "Unrecognized connection type")
            raise NotImplementedError(message)

        stream_conf = StreamConfiguration(
            name=dialog.stream_name.text(),
            connection_type=dialog.connection_type,
            connection_options=params,
            premises_id=premises_id,
            runtime_options={
                "keyframes_only": keyframes_only
            },
            metadata={})

        if dialog.connection_type == StreamConfiguration.ConnType.FILE:
            # Kick off file uploading asynchronously
            filepath = Path(dialog.parameter_value.text())

            def on_file_uploaded(storage_id):
                stream_conf.connection_options["storage_id"] = storage_id
                on_success(stream_conf)

            try:
                cls._upload_file(
                    filepath,
                    on_file_uploaded,
                    on_error,
                    parent)
            except CanceledError:
                # The upload was cancelled by the user
                return None
        else:
            # Nothing blocking to do, just synchronously report success
            on_success(stream_conf)

    @pyqtSlot(int)
    def connection_type_changed_slot(self, connection_index: int):
        """Called when connection_type_combo_box's index is changed"""
        if connection_index == 0:
            self.connection_type = None

            # Hide parameter widgets
            self._set_parameter_widgets_hidden(True)
        else:

            if connection_index == 1:  # IP Camera
                self.connection_type = StreamConfiguration.ConnType.IP_CAMERA
                self.parameter_label.setText(self.tr("Camera web address"))
                self._set_premises_options_hidden(False)
                self._update_premises_combobox()

            elif connection_index == 2:  # Webcam
                self.connection_type = StreamConfiguration.ConnType.WEBCAM
                self.parameter_label.setText(self.tr("Device ID"))
                self._set_premises_options_hidden(True)
            elif connection_index == 3:  # File
                # TODO(Bryce Beagle): Use QFileDialog
                self.connection_type = StreamConfiguration.ConnType.FILE
                self._set_premises_options_hidden(True)
                self.parameter_label.setText(self.tr("Filepath"))

            # Show parameter widgets
            self._set_parameter_widgets_hidden(False)
            # Show advanced options
            self._set_advanced_options_section_hidden(False)

    @pyqtSlot()
    def verify_inputs_valid(self):
        """Verify that the dialogs inputs have been filled. Allows the "OK"
        button to be clicked if everything looks valid.

        Connected to:
        - QTextEdit -- Dynamic
          self.stream_name.textChanged
        - QComboBox -- Dynamic
          self.connection_type_combo_box.currentTextChanged
        - QCheckBox -- Dynamic
          self.advanced_options_checkbox.stateChanged
        - QCheckBox -- Dynamic
          self.avoid_transcoding_checkbox.stateChanged
        - QTextEdit -- Dynamic
          self.parameter_value.textChanged
        """
        is_valid = True

        if self.stream_name.text().strip() == "":
            is_valid = False

        if self.connection_type is None or self.parameter_value.text() == "":
            is_valid = False

        # Check that a URL field is in the pipeline if the pipeline is being
        # used
        if self.connection_type == StreamConfiguration.ConnType.IP_CAMERA \
                and self.advanced_options_checkbox.isChecked() \
                and self.pipeline_value.text() \
                and "{url}" not in self.pipeline_value.text():
            is_valid = False

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(is_valid)

    @pyqtSlot()
    def update_advanced_option_items(self):
        """Changes whether or not the advanced options are hidden based on the
        value of the "Advanced Options" checkbox and the currently selected
        stream type.

        Connected to:
        - QCheckBox -- Dynamic
          self.advanced_options_checkbox.stateChanged
        """
        # If the whole advanced options section is hidden, hide the actual
        # options regardless of the checkbox value
        section_hidden = self.advanced_options_checkbox.isHidden()
        # Even if the advanced options section should be shown, the actual
        # options will not be shown if the advanced options checkbox is
        # unchecked
        unchecked = not self.advanced_options_checkbox.isChecked()

        # Advanced options for all stream types
        self.pipeline_label.setHidden(section_hidden or unchecked)
        self.pipeline_value.setHidden(section_hidden or unchecked)

        # Advanced options for the IP camera stream type
        self.keyframe_only_checkbox.setHidden(
            section_hidden
            or unchecked
            or self.connection_type is not StreamConfiguration.ConnType.IP_CAMERA)

        # Advanced options for the file stream type
        self.avoid_transcoding_checkbox.setHidden(
            section_hidden
            or unchecked
            or self.connection_type is not StreamConfiguration.ConnType.FILE)

    def _update_premises_combobox(self):
        # Set the premises dropdown options
        self.premises_combobox.clear()
        premises_options = [(self.tr("Local Network"), None)] + \
                           [(p.name, p.id) for p in api.get_all_premises()]
        for premises_name, premises_id in premises_options:
            self.premises_combobox.addItem(premises_name, premises_id)

    def _set_parameter_widgets_hidden(self, hidden):
        """Hide or show the widgets related to the parameters

        This is used because we don't want to show the parameter options until
        we know what options to display. They are connection type dependent.
        """
        self.parameters_container.setHidden(hidden)

        # Hide the file selection button if selected connection type is not
        # file
        self.select_file_button.setHidden(
            self.connection_type != StreamConfiguration.ConnType.FILE)

    def _set_premises_options_hidden(self, hidden):
        self.premises_label.setHidden(hidden)
        self.premises_combobox.setHidden(hidden)

    def _set_advanced_options_section_hidden(self, hidden):
        """Hide or show the advanced options section.
        """
        self.advanced_options_checkbox.setHidden(hidden)
        self.update_advanced_option_items()

    def _file_dialog(self):
        """Get the path to (presumably) a video file"""

        # Second return value is ignored. PyQt5 returns what appears to be a
        # filter as a string as well, differing from the C++ implementation
        file_path, _ = QFileDialog().getOpenFileName(
            self,
            self.tr("Select video file"),
            QStandardPaths.writableLocation(QStandardPaths.HomeLocation))

        self.parameter_value.setText(file_path)

    @staticmethod
    def _upload_file(filepath: Path,
                     on_success: Callable[[Optional[int]], None],
                     on_error: Callable[[Exception], None],
                     parent: QObject) -> None:
        """Uploads a file to storage asynchronously, notifying the user of the
        upload progress using a QProgressDialog. If the user cancels the
        process, no callback will be called.

        :param filepath: The path to the file to upload
        :param on_success: Called when the file is done uploading, providing
            the storage ID
        :param on_error: Called if there was an error while uploading
        :param parent: The parent element
        """
        reader = ProgressFileReader(filepath, parent)

        # Make the progress dialog
        label_text = parent.tr("Uploading {filepath}...".format(
            filepath=filepath
        ))
        progress_dialog = QProgressDialog(parent)
        progress_dialog.setLabelText(label_text)
        # progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setMinimum(0)
        progress_dialog.setMaximum(reader.file_size)
        progress_dialog.setValue(0)
        progress_dialog.setMinimumDuration(0)

        # Connect signals
        reader.progress_signal.connect(progress_dialog.setValue)
        progress_dialog.canceled.connect(reader.cancel)

        def upload_video() -> Optional[int]:
            try:
                with reader:
                    return api.new_storage(reader, "application/octet-stream")
            except CanceledError:
                # The user canceled the upload
                return None

        def on_success_check_none(storage_id: Optional[int]):
            # Make sure the progress dialog closes
            progress_dialog.cancel()
            if storage_id is not None:
                on_success(storage_id)

        QTAsyncWorker(parent,
                      upload_video,
                      on_success=on_success_check_none,
                      on_error=on_error).start()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = StreamConfigurationDialog()
    window.show()

    app.exec_()
