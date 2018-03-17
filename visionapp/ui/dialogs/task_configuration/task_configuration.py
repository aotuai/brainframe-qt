from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

from ui.dialogs.alarm_creation.alarm_creation import AlarmCreationDialog
from ui.dialogs.task_configuration.zone_list.zone_and_tasks.zone_and_tasks \
    import ZoneAndTasks


class TaskConfiguration(QWidget):

    def __init__(self, parent):

        super().__init__(parent)

        loadUi("ui/dialogs/task_configuration/task_configuration.ui", self)

    @pyqtSlot()
    def new_alarm(self):
        alarm = AlarmCreationDialog.new_alarm(self.zone_list.get_zones())
        if not alarm:
            return

        self.zone_list.add_alarm(alarm)

    @pyqtSlot()
    def new_region(self):
        self.zone_list.add_zone(ZoneAndTasks("Test Region", "region",
                                             self.zone_list))

    @pyqtSlot()
    def new_line(self):
        self.zone_list.add_zone(ZoneAndTasks("Test Region", "line",
                                             self.zone_list))


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = TaskConfiguration(None)
    window.show()

    app.exec_()
