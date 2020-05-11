from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QInputDialog,
                             QMessageBox)
from PyQt5.uic import loadUi
from brainframe.client.api_helpers import api
from brainframe.api.codecs import StreamConfiguration, Zone
from brainframe.client.ui.dialogs import AlarmCreationDialog
from brainframe.client.ui.resources import QTAsyncWorker
from brainframe.client.ui.resources.paths import qt_ui_paths


class TaskConfiguration(QDialog):
    def __init__(self, parent=None, stream_conf=None):
        """There should _always_ be a stream_configuration passed here. The
        reason it is None is to allow compatibility with QTDesigner."""
        super().__init__(parent)

        loadUi(qt_ui_paths.task_configuration_ui, self)

        # If not running within QTDesigner, run logic
        self.stream_conf: StreamConfiguration = stream_conf
        if stream_conf:
            self.video_task_config.change_stream(stream_conf)
            self.stream_name_label.setText(stream_conf.name)

            # Create TaskAndZone widgets in ZoneList for zones in database
            self.zone_list.init_zones(stream_conf.id)

        self.unconfirmed_zone: Zone = None

        self._hide_operation_widgets(True)

        self.cancel_op_button.clicked.connect(self.new_region_canceled)

    @classmethod
    def open_configuration(cls, stream_conf, parent):
        dialog = cls(parent=parent, stream_conf=stream_conf)
        result = dialog.exec_()

        return result

    @pyqtSlot()
    def new_alarm(self):

        def get_plugins_and_zones():
            plugins = api.get_plugins()
            zones = api.get_zones(self.stream_conf.id)
            return plugins, zones

        def create_alarm(plugins_and_zones):
            plugins, zones = plugins_and_zones

            zone, alarm = AlarmCreationDialog.new_alarm(
                self, zones=zones, plugins=plugins)

            if not alarm:
                return

            def set_zone_alarm():
                return api.set_zone_alarm(alarm)

            def add_alarm(new_alarm):
                self.zone_list.add_alarm(zone, new_alarm)

            QTAsyncWorker(self, set_zone_alarm, on_success=add_alarm).start()

        QTAsyncWorker(self, get_plugins_and_zones,
                      on_success=create_alarm) \
            .start()

    @pyqtSlot()
    def new_line(self):
        line_name = self.get_new_zone_name(
            self.tr("New Line"),
            self.tr("Name for new line:"))
        if line_name is None:
            return
        self.new_zone(line_name, max_points=2)

    @pyqtSlot()
    def new_region(self):
        region_name = self.get_new_zone_name(
            self.tr("New Region"),
            self.tr("Name for new region:"))
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

        # Update zone type
        if len(self.unconfirmed_zone.coords) == 2:
            zone_type = self.zone_list.EntryType.LINE
        elif len(self.unconfirmed_zone.coords) >= 2:
            zone_type = self.zone_list.EntryType.REGION
        else:
            message = self.tr("New zone cannot have fewer than 2 points")
            raise NotImplementedError(message)

        # Add zone to database
        zone = api.set_zone(self.unconfirmed_zone)

        self.zone_list.zones[zone.id] = self.zone_list.zones.pop(None)
        self.zone_list.update_zone_type(zone.id, zone_type)

        self.zone_list.zones[zone.id].trash_button.clicked.connect(
            lambda: self.zone_list.delete_zone(zone.id)
        )

        self.unconfirmed_zone = None

        self._set_widgets_enabled(True)
        self._hide_operation_widgets(True)

    @pyqtSlot()
    def new_region_canceled(self):
        if None in self.zone_list.zones:
            # Remove instruction text
            self.instruction_label.setText("")

            # Delete unconfirmed zone
            self.zone_list.delete_zone(None)

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
        text = self.tr('Add points until done, then press "Confirm" button')
        self.instruction_label.setText(text)

        # Add the a Zone widget to the sidebar
        unconfirmed_zone_item = self.zone_list.add_zone(self.unconfirmed_zone)

        # Allow delete button on new zone widget in zone list to cancel the new
        # zone
        unconfirmed_zone_item.trash_button.clicked.disconnect()
        unconfirmed_zone_item.trash_button.clicked.connect(
            self.new_region_canceled
        )

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
                title = self.tr("Item Name Already Exists")
                message = self.tr("Item {} already exists in Stream").format(
                    region_name)
                message += "<br>" + self.tr("Please use another name.")
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
