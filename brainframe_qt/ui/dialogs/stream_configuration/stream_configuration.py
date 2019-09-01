from PyQt5.QtCore import Qt, pyqtSlot, QStandardPaths
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog,
    QDialogButtonBox,
    QComboBox,
    QLineEdit,
    QPushButton,
    QCheckBox
)
from PyQt5.uic import loadUi

from brainframe.client.ui.resources.paths import image_paths, qt_ui_paths
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
        self.verify_inputs_valid()

        self.advanced_options_checkbox.stateChanged.connect(
            self.toggle_advanced_options)

        # Start with advanced options hidden
        self.toggle_advanced_options()

    @classmethod
    def configure_stream(cls, parent, stream_conf=None):
        dialog = cls(parent, stream_conf)
        result = dialog.exec_()

        if not result:
            return None

        premises_id = None
        if dialog.connection_type == StreamConfiguration.ConnType.IP_CAMERA:
            url = str(dialog.parameter_value.text()).strip()
            params = {"url": url}
            # Add the pipeline value if it was configured
            pipeline = str(dialog.pipeline_value.text())
            if dialog.advanced_options_checkbox.isChecked() and pipeline:
                params["pipeline"] = pipeline

            premises_id = dialog.premises_combobox.itemData(
                dialog.premises_combobox.currentIndex())
        elif dialog.connection_type == StreamConfiguration.ConnType.WEBCAM:
            device_id = str(dialog.parameter_value.text()).strip()
            params = {"device_id": device_id}
        elif dialog.connection_type == StreamConfiguration.ConnType.FILE:
            params = {"filepath": str(dialog.parameter_value.text())}
        else:
            message = QApplication.translate('StreamConfigurationDialog',
                                             "Unrecognized connection type")
            raise NotImplementedError(message)

        keyframes_only = dialog.advanced_options_checkbox.isChecked() \
                         and dialog.keyframe_only_checkbox.isChecked()
        return StreamConfiguration(
            name=dialog.stream_name.text(),
            connection_type=dialog.connection_type,
            connection_options=params,
            premises_id=premises_id,
            runtime_options={
                "keyframes_only": keyframes_only
            })

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
                self._set_advanced_options_section_hidden(False)
                self._update_premises_combobox()

            elif connection_index == 2:  # Webcam
                self.connection_type = StreamConfiguration.ConnType.WEBCAM
                self.parameter_label.setText(self.tr("Device ID"))
                self._set_premises_options_hidden(True)
                self._set_advanced_options_section_hidden(True)
            elif connection_index == 3:  # File
                # TODO(Bryce Beagle): Use QFileDialog
                self.connection_type = StreamConfiguration.ConnType.FILE
                self._set_premises_options_hidden(True)
                self.parameter_label.setText(self.tr("Filepath"))
                self._set_advanced_options_section_hidden(True)

            # Show parameter widgets
            self._set_parameter_widgets_hidden(False)

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
    def toggle_advanced_options(self):
        """Changes whether or not the advanced options are hidden based on the
        value of the "Advanced Options" checkbox.

        Connected to:
        - QCheckBox -- Dynamic
          self.advanced_options_checkbox.stateChanged
        """
        hidden = not self.advanced_options_checkbox.isChecked()
        self.pipeline_label.setHidden(hidden)
        self.pipeline_value.setHidden(hidden)
        self.keyframe_only_checkbox.setHidden(hidden)

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
        if hidden:
            # If the whole advanced options section is hidden, hide the actual
            # options regardless of the checkbox value
            self.pipeline_label.setHidden(hidden)
            self.pipeline_value.setHidden(hidden)
            self.keyframe_only_checkbox.setHidden(hidden)
        else:
            # Even if the advanced options section should be shown, the actual
            # options may or may not be visible based on the checkbox value
            self.toggle_advanced_options()

    def _file_dialog(self):
        """Get the path to (presumably) a video file"""

        # Second return value is ignored. PyQt5 returns what appears to be a
        # filter as a string as well, differing from the C++ implementation
        file_path, _ = QFileDialog().getOpenFileName(
            self,
            self.tr("Select video file"),
            QStandardPaths.writableLocation(QStandardPaths.HomeLocation))

        self.parameter_value.setText(file_path)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = StreamConfigurationDialog()
    window.show()

    app.exec_()
