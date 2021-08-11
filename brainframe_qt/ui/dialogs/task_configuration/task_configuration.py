from typing import Optional

from PyQt5.QtCore import pyqtSlot, QObject
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QInputDialog
from PyQt5.uic import loadUi

from brainframe.api import bf_codecs

from brainframe_qt.api_utils import api
from brainframe_qt.ui.dialogs import AlarmCreationDialog
from brainframe_qt.ui.resources import QTAsyncWorker
from brainframe_qt.ui.resources.paths import qt_ui_paths
from brainframe_qt.ui.resources.ui_elements.widgets.dialogs import BrainFrameMessage

from .core.zone import Zone, Line, Region


class TaskConfiguration(QDialog):
    def __init__(self, stream_conf: bf_codecs.StreamConfiguration, *, parent: QObject):
        super().__init__(parent=parent)

        loadUi(qt_ui_paths.task_configuration_ui, self)

        self.stream_conf = stream_conf
        self.video_task_config.change_stream(stream_conf)
        self.stream_name_label.setText(stream_conf.name)

        # Create TaskAndZone widgets in ZoneList for zones in database
        self.zone_list.init_zones(stream_conf.id)

        self.unconfirmed_zone: Optional[Zone] = None

        self._hide_operation_widgets(True)

        self._init_signals()

    def _init_signals(self) -> None:
        self.cancel_op_button.clicked.connect(self.cancel_zone_edit)
        self.new_line_button.clicked.connect(lambda _clicked: self.new_line())
        self.new_region_button.clicked.connect(lambda _clicked: self.new_region())

        self.zone_list.initiate_zone_edit.connect(self.edit_zone)

    @classmethod
    def open_configuration(cls, stream_conf, parent):
        dialog = cls(stream_conf=stream_conf, parent=parent)
        result = dialog.exec_()

        return result

    @pyqtSlot()
    def new_alarm(self):

        def get_capsules_and_zones():
            capsules = api.get_capsules()
            zones = api.get_zones(self.stream_conf.id)
            return capsules, zones

        def create_alarm(capsules_and_zones):
            capsules, zones = capsules_and_zones

            zone, alarm = AlarmCreationDialog.new_alarm(
                self, zones=zones, capsules=capsules)

            if not alarm:
                return

            def set_zone_alarm():
                return api.set_zone_alarm(alarm)

            def add_alarm(new_alarm):
                self.zone_list.add_alarm(zone, new_alarm)

            QTAsyncWorker(self, set_zone_alarm, on_success=add_alarm).start()

        QTAsyncWorker(self, get_capsules_and_zones,
                      on_success=create_alarm) \
            .start()

    def new_line(self) -> None:
        line_name = self.get_new_zone_name(
            self.tr("New Line"),
            self.tr("Name for new line:"))
        if line_name is None:
            return

        line = Line(name=line_name, coords=[])

        self.new_zone(line)

    def new_region(self) -> None:
        region_name = self.get_new_zone_name(
            self.tr("New Region"),
            self.tr("Name for new region:"))
        if region_name is None:
            return

        region = Region(name=region_name, coords=[])

        self.new_zone(region)

    def new_zone(self, zone: Zone) -> None:
        self.edit_zone(zone)

        # Add the a Zone widget to the sidebar
        unconfirmed_zone_item = self.zone_list.add_zone(self.unconfirmed_zone)

        # Allow delete button on new zone widget in zone list to cancel the new zone
        unconfirmed_zone_item.trash_button.clicked.disconnect()
        unconfirmed_zone_item.trash_button.clicked.connect(self.cancel_zone_edit)

    @pyqtSlot()
    def confirm_zone_edit(self) -> None:
        self.instruction_label.setText("")

        # Instruct the VideoTaskConfig to confirm the unconfirmed zone and return its
        # coordinates
        self.unconfirmed_zone.coords = self.video_task_config.confirm_zone_edit()

        """List of based point tuples
        
        Eg. [(0, 0), (100, 0), (100, 100), (0, 100)]
        """

        # Update zone type
        if len(self.unconfirmed_zone.coords) == 2:
            zone_type = self.zone_list.EntryType.LINE
        elif len(self.unconfirmed_zone.coords) >= 2:
            zone_type = self.zone_list.EntryType.REGION
        else:
            message = "New zone cannot have fewer than 2 points"
            raise NotImplementedError(message)

        # Add zone to database
        api_zone = self.unconfirmed_zone.to_api_zone(self.stream_conf.id)
        confirmed_zone = Zone.from_api_zone(api.set_zone(api_zone))

        # Only do this for new zones
        if self.unconfirmed_zone.id is None:
            self.zone_list.zones[confirmed_zone.id] = self.zone_list.zones.pop(None)
            self.zone_list.update_zone_type(confirmed_zone.id, zone_type)

            self.zone_list.zones[confirmed_zone.id].trash_button.clicked.connect(
                lambda: self.zone_list.delete_zone(confirmed_zone.id)
            )

        self.unconfirmed_zone = None

        self._set_widgets_enabled(True)
        self._hide_operation_widgets(True)

    def cancel_zone_edit(self) -> None:
        # Remove instruction text
        self.instruction_label.setText("")

        # Instruct the VideoTaskConfig instance to delete its unconfirmed zone
        self.video_task_config.discard_zone_edit()

        self._set_widgets_enabled(True)
        self._hide_operation_widgets(True)

        if None in self.zone_list.zones:
            self.zone_list.delete_zone(None)

    def edit_zone(self, zone: Zone) -> None:
        """Create a new zone"""
        self.unconfirmed_zone = zone.copy()

        # Set instruction text
        text = self.tr('Add points until done, then press "Confirm" button')
        self.instruction_label.setText(text)

        # Instruct the VideoTaskConfig instance to start accepting mouseEvents
        self.video_task_config.start_zone_edit(zone)

        # Disable critical widgets from being interacted with during creation
        self._set_widgets_enabled(False)
        self._hide_operation_widgets(False)

        # Disable confirmation until the zone has enough points to be valid
        self.confirm_op_button.setEnabled(False)

    @pyqtSlot(bool)
    def enable_confirm_op_button(self, enable) -> None:
        self.confirm_op_button.setEnabled(enable)

    def get_new_zone_name(self, prompt_title: str, prompt_text: str) -> Optional[str]:
        """Get the name for a new zone, while checking if it exists"""
        while True:
            region_name, ok = QInputDialog.getText(self, prompt_title, prompt_text)
            if not ok:
                # User pressed cancel or escape or otherwise closed the window without
                # pressing Ok
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
                    region_name
                )
                message += "<br>" + self.tr("Please use another name.")

                BrainFrameMessage.information(
                    parent=self,
                    title=title,
                    message=message
                ).exec()

                continue

            break
        return region_name

    def _set_widgets_enabled(self, enabled) -> None:
        # TODO(Bryce Beagle): Do this dynamically:
        # https://stackoverflow.com/a/34892529/8134178

        self.dialog_button_box.button(QDialogButtonBox.Ok).setEnabled(enabled)
        self.alarm_button.setEnabled(enabled)
        self.new_line_button.setEnabled(enabled)
        self.new_region_button.setEnabled(enabled)

    def _hide_operation_widgets(self, hidden) -> None:
        self.confirm_op_button.setHidden(hidden)
        self.cancel_op_button.setHidden(hidden)
        self.instruction_label.setHidden(hidden)
