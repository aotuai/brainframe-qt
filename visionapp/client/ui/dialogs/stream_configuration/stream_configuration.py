from enum import Enum

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

from visionapp.client.ui.resources.paths import qt_ui_paths


class StreamConfiguration(QDialog):
    """Dialog for configuring a Stream"""

    # noinspection PyArgumentList
    # PyCharm incorrectly complains
    ConnectionType = Enum("ConnectionType",
                          "unconfigured ip_camera webcam file")

    def __init__(self, parent=None, stream_conf=None):

        super().__init__(parent)

        loadUi(qt_ui_paths.stream_configuration_ui, self)

        if stream_conf:
            pass
        else:
            self.connection_type = self.ConnectionType.unconfigured

        if self.connection_type == self.ConnectionType.unconfigured:
            self._set_parameter_widgets_hidden(True)

    @pyqtSlot(str)
    def connection_type_changed_slot(self, connection_type):
        """Called when connection_type_combo_box's value is changed"""
        if connection_type == "":
            self.connection_type = self.ConnectionType.unconfigured

            # Hide parameter widgets
            self._set_parameter_widgets_hidden(True)

        else:
            # Show parameter widgets
            self._set_parameter_widgets_hidden(False)

            if connection_type == "IP Camera":
                self.connection_type = self.ConnectionType.ip_camera
                self.parameter_label.setText("Camera <b>address[:port]</b>")
            elif connection_type == "Webcam":
                self.connection_type = self.ConnectionType.webcam
                self.parameter_label.setText("Device ID")
            elif connection_type == "File":
                # TODO: Use QFileDialog
                self.connection_type = self.ConnectionType.file
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
    window = StreamConfiguration()
    window.show()

    app.exec_()
