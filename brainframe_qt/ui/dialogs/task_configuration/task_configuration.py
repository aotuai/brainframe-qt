from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QInputDialog, QDialogButtonBox, QMessageBox
from PyQt5.uic import loadUi

from brainframe.client.api import api
from brainframe.client.api.codecs import Zone, StreamConfiguration
from brainframe.client.ui.resources.paths import qt_ui_paths
from brainframe.client.ui.dialogs import AlarmCreationDialog


class TaskConfiguration(QDialog):
    def __init__(self, parent=None, stream_conf=None):
        """There should _always_ be a stream_configuration passed here. The
        reason it is None is to allow compatibility with QTDesigner."""
        super().__init__(parent)

        loadUi(qt_ui_paths.task_configuration_ui, self)

        # If not running within QTDesigner, run logic
        self.stream_conf = stream_conf  # type: StreamConfiguration
        if stream_conf:
            self.video_task_config.change_stream(stream_conf)
            self.stream_name_label.setText(stream_conf.name)

            # Create TaskAndZone widgets in ZoneList for zones in database
            self.zone_list.init_zones(stream_conf.id)

        self.unconfirmed_zone = None  # type: Zone
        self.unconfirmed_zone_widget = None

        self._hide_operation_widgets(True)

    @classmethod
    def open_configuration(cls, stream_conf):
        dialog = cls(stream_conf=stream_conf)

        dialog.video_task_config.change_stream(stream_conf)

        result = dialog.exec_()

        return result

    @pyqtSlot()
    def new_alarm(self):

        engine_config = api.get_engine_configuration()
        zones = api.get_zones(self.stream_conf.id)

        zone, alarm = AlarmCreationDialog.new_alarm(zones=zones,
                                                    engine_config=engine_config)
        if not alarm:
            return None

        zone = api.set_zone(self.stream_conf.id, zone)
        self.zone_list.add_alarm(zone, alarm)

    @pyqtSlot()
    def new_line(self):
        print("new line called")
        line_name = self.get_new_zone_name("New Line",
                                           "Name for new line:")

        if line_name is None:
            return
        self.new_zone(line_name, max_points=2)

    @pyqtSlot()
    def new_region(self):
        region_name = self.get_new_zone_name("New Region",
                                             "Name for new region:")
        if region_name is None:
            return
        self.new_zone(region_name)

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
        self.unconfirmed_zone_widget.update_zone_type()
        # Add zone to database
        zone = api.set_zone(self.stream_conf.id, self.unconfirmed_zone)
        self.unconfirmed_zone_widget.zone = zone

        self.zone_list.zones[zone.id] = self.zone_list.zones.pop(None)
        self.unconfirmed_zone_widget.zone_deleted_signal.connect(
            self.zone_list.delete_zone)

        # Clear unconfirmed zone now that we're done with it
        self.unconfirmed_zone = None
        self.unconfirmed_zone_widget = None

        self._set_widgets_enabled(True)
        self._hide_operation_widgets(True)

    @pyqtSlot()
    def new_region_canceled(self):

        # Remove instruction text
        self.instruction_label.setText("")

        # Tell ZoneList to delete widget
        self.zone_list.delete_zone_widget(self.unconfirmed_zone.id)

        # Delete unconfirmed zone
        self.unconfirmed_zone = None
        self.unconfirmed_zone_widget.deleteLater()
        self.unconfirmed_zone_widget = None

        # Instruct the VideoTaskConfig instance to delete its unconfirmed
        # polygon
        self.video_task_config.clean_up()

        self._set_widgets_enabled(True)
        self._hide_operation_widgets(True)

    def new_zone(self, new_zone_name, max_points=None):
        """Create a new zone (either line or region)"""
        # Create a new Zone
        self.unconfirmed_zone = Zone(name=new_zone_name,
                                     stream_id=self.stream_conf.id,
                                     coords=[])

        # Set instruction text
        self.instruction_label.setText(
            'Add points until done, then press "Confirm" button')

        # Add the a Zone widget to the sidebar
        self.unconfirmed_zone_widget = self.zone_list.add_zone(
            self.unconfirmed_zone)

        # Allow delete button on new zone widget in zone list to cancel the new
        # zone
        self.unconfirmed_zone_widget.zone_deleted_signal.connect(
            self.new_region_canceled)

        # Instruct the VideoTaskConfig instance to start accepting mouseEvents
        self.video_task_config.start_new_polygon(max_points)

        # Disable critical widgets from being interacted with during creation
        self._set_widgets_enabled(False)
        self._hide_operation_widgets(False)

    @pyqtSlot(bool)
    def enable_confirm_op_button(self, enable):
        self.confirm_op_button.setEnabled(enable)

    def get_new_zone_name(self, prompt_title, prompt_text):
        """Get the name for a new zone, while checking if it exists"""
        while True:
            region_name, ok = QInputDialog.getText(self, prompt_title,
                                                   prompt_text)
            if not ok:
                # User pressed cancel or escape or otherwise closed the window
                # without pressing Ok
                return None

            # Strip whitespace as a favor for the user
            region_name = region_name.strip()

            # TODO(Bryce Beagle): Grey out QInputDialog Ok button if no entry
            # instead
            if region_name == "":
                # Return if entered string is empty
                return None

            zones = api.get_zones(self.stream_conf.id)
            if region_name in [zone.name for zone in zones]:
                title = "Item Name Already Exists"
                message = "Item {} already exists in Stream".format(region_name)
                message += "<br>Please use another name."
                QMessageBox.information(self, title, message)
                continue

            break
        return region_name

    def _set_widgets_enabled(self, enabled):
        # TODO(Bryce Beagle): Do this dynamically:
        # https://stackoverflow.com/a/34892529/8134178

        self.dialog_button_box.button(QDialogButtonBox.Ok).setEnabled(enabled)
        self.alarm_button.setEnabled(enabled)
        self.line_button.setEnabled(enabled)
        self.region_button.setEnabled(enabled)

    def _hide_operation_widgets(self, hidden):
        self.confirm_op_button.setHidden(hidden)
        self.cancel_op_button.setHidden(hidden)
        self.instruction_label.setHidden(hidden)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = TaskConfiguration(None)
    window.show()

    app.exec_()