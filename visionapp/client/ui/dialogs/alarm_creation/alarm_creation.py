from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

from ui.resources.datatypes.alarm import Alarm


class AlarmCreationDialog(QDialog):

    def __init__(self, zone_list=None, parent=None):
        super().__init__(parent)

        loadUi("ui/dialogs/alarm_creation/alarm_creation.ui", self)

        if zone_list:
            self.zone_combo_box.clear()
            self.zone_combo_box.addItems(zone_list)

    @classmethod
    def new_alarm(cls, zone_list=None):
        dialog = cls(zone_list, None)
        result = dialog.exec_()

        if not result:
            return None

        data = {"alarm_name": dialog.alarm_name.text(),
                "test_type": dialog.test_type_combo_box.currentText(),
                "count": dialog.count_spin_box.value,
                "countable": dialog.countable_combo_box.currentText(),
                "behavior": dialog.behavior_combo_box.currentText(),
                "zone": dialog.zone_combo_box.currentText(),
                "start_time": dialog.start_time_edit.time(),
                "stop_time": dialog.stop_time_edit.time()}

        return Alarm(**data)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = AlarmCreationDialog(None)
    window.show()

    app.exec_()
