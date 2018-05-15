from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

from brainframe.client.ui.resources.paths import qt_ui_paths
from brainframe.client.api.codecs import StreamConfiguration


class StreamConfigurationDialog(QDialog):
    """Dialog for configuring a Stream"""

    def __init__(self, parent=None, stream_conf=None):

        super().__init__(parent)

        loadUi(qt_ui_paths.stream_configuration_ui, self)

        if stream_conf:
            pass
        else:
            self.connection_type = None

        if self.connection_type is None:
            self._set_parameter_widgets_hidden(True)

    @classmethod
    def configure_stream(cls, stream_conf=None):
        dialog = cls(stream_conf)
        result = dialog.exec_()

        if not result:
            return None

        if dialog.connection_type == StreamConfiguration.ConnType.ip_camera:
            params = {"url": "{}".format(dialog.parameter_value.text())}
        elif dialog.connection_type == StreamConfiguration.ConnType.webcam:
            params = {"device_id": "{}".format(dialog.parameter_value.text())}
        elif dialog.connection_type == StreamConfiguration.ConnType.file:
            params = {"filepath": "{}".format(dialog.parameter_value.text())}
        else:
            raise NotImplementedError("Unrecognized connection type")

        return StreamConfiguration(name=dialog.stream_name.text(),
                                   connection_type=dialog.connection_type,
                                   parameters=params)

    @pyqtSlot(str)
    def connection_type_changed_slot(self, connection_type):
        """Called when connection_type_combo_box's value is changed"""
        if connection_type == "":
            self.connection_type = None

            # Hide parameter widgets
            self._set_parameter_widgets_hidden(True)

        else:
            # Show parameter widgets
            self._set_parameter_widgets_hidden(False)

            if connection_type == "IP Camera":
                self.connection_type = StreamConfiguration.ConnType.ip_camera
                self.parameter_label.setText("Camera web address")
            elif connection_type == "Webcam":
                self.connection_type = StreamConfiguration.ConnType.webcam
                self.parameter_label.setText("Device ID")
            elif connection_type == "File":
                # TODO(Bryce Beagle): Use QFileDialog
                self.connection_type = StreamConfiguration.ConnType.file
                self.parameter_label.setText("Filepath")

    def _set_parameter_widgets_hidden(self, hidden):
        """Hide or show the widgets related to the parameters

        This is used because we don't want to show the parameter options until
        we know what options to display. They are connection type dependent.
        """
        self.stream_options_label.setHidden(hidden)
        self.parameter_label.setHidden(hidden)
        self.parameter_value.setHidden(hidden)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = StreamConfigurationDialog()
    window.show()

    app.exec_()
