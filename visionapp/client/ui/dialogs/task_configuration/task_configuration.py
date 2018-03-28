from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QInputDialog, QDialogButtonBox
from PyQt5.uic import loadUi

from visionapp.client.api.codecs import Zone
from visionapp.client.ui.resources.paths import qt_ui_paths
from visionapp.client.ui.dialogs import AlarmCreationDialog
from .zone_list import ZoneList


class TaskConfiguration(QDialog):

    def __init__(self, parent=None, stream_conf=None):

        super().__init__(parent)

        loadUi(qt_ui_paths.task_configuration_ui, self)

        self.stream_conf = stream_conf if stream_conf else None
        if stream_conf:
            self.video_task_config.change_stream(stream_conf)

        self.unconfirmed_zone: Zone = None

    @classmethod
    def open_configuration(cls, stream_conf):
        dialog = cls(stream_conf=stream_conf)

        dialog.video_task_config.change_stream(stream_conf)

        result = dialog.exec_()

        return result

    @pyqtSlot()
    def new_alarm(self):
        alarm = AlarmCreationDialog.new_alarm(self.zone_list.get_zones())
        if not alarm:
            return

        self.zone_list.add_alarm(alarm)

    @pyqtSlot()
    def new_region(self):

        region_name, ok = QInputDialog.getText(QInputDialog(), "New Zone",
                                               "Name for new zone:")
        if not ok:
            # User pressed cancel or escape or otherwise closed the window
            # without pressing Ok
            return

        # TODO: Grey out QInputDialog Ok button if no entry instead
        if region_name == "":
            # Return if entered string is empty
            return

        # Create a new Zone
        self.unconfirmed_zone = Zone(name=region_name, coords=[])

        # Set instruction text
        self.instruction_label.setText(
            'Add points until done, then press "Confirm" button')

        # Add the a Zone widget to the sidebar
        self.unconfirmed_zone_widget = self.zone_list.add_zone(
            self.unconfirmed_zone)

        # Instruct the VideoTaskConfig instance to start accepting mouseEvents
        self.video_task_config.start_new_polygon()

        # Disable critical widgets from being interacted with during creation
        self._set_widgets_enabled(False)

    @pyqtSlot()
    def new_region_confirmed(self):
        self.instruction_label.setText("")

        # Instruct the VideoTaskConfig to confirm the unconfirmed polygon and
        # return its polygon for its points
        polygon = self.video_task_config.confirm_unconfirmed_polygon()

        self.unconfirmed_zone.coords = [(pt.x(), pt.y()) for pt in polygon]
        """List of based point tuples
        
        Eg. [(0, 0), (100, 0), (100, 100), (0, 100)]
        """

        # Make ZoneAndTasks widget re-evaluate it's zone_type
        # TODO: THIS WAS THE LAST THING I WAS WORKING ON
        # self.unconfirmed_zone.update_zone_type()

        # Clear unconfirmed zone now that we're done with it
        self.unconfirmed_zone = None

        self._set_widgets_enabled(True)

    @pyqtSlot()
    def new_region_canceled(self):

        # Remove instruction text
        self.instruction_label.setText("")

        # Delete unconfirmed zone
        self.unconfirmed_zone = None

        # Instruct the VideoTaskConfig instance to delete its unconfirmed
        # polygon
        self.video_task_config.remove_unconfirmed_polygon()

        self._set_widgets_enabled(True)

    @pyqtSlot()
    def new_line(self):
        self.zone_list.add_zone("Test Region", ZoneList.TaskType.line)

    def _set_widgets_enabled(self, enabled):
        # TODO: Do this dynamically:
        # https://stackoverflow.com/a/34892529/8134178

        self.dialog_button_box.button(QDialogButtonBox.Ok).setEnabled(enabled)
        self.alarm_button.setEnabled(enabled)
        self.line_button.setEnabled(enabled)
        self.region_button.setEnabled(enabled)
        self.detect_behavior_checkbox.setEnabled(enabled)
        self.crowd_heatmap_checkbox.setEnabled(enabled)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = TaskConfiguration(None)
    window.show()

    app.exec_()
