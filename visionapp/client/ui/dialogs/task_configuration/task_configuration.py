from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

from ui.resources import client_paths
from ui.dialogs import AlarmCreationDialog
# TODO: Shorten (most likely with an __init__.py)
from ui.dialogs.task_configuration.zone_list.zone_and_tasks.zone_and_tasks \
    import ZoneAndTasks


class TaskConfiguration(QDialog):

    def __init__(self, parent=None, stream_conf=None):

        super().__init__(parent)

        loadUi(client_paths.task_configuration_ui, self)

        self.stream_conf = stream_conf if stream_conf else None
        if stream_conf:
            self.video.change_stream(stream_conf)

    @classmethod
    def open_configuration(cls, stream_conf):
        dialog = cls(stream_conf=stream_conf)

        dialog.video.change_stream(stream_conf)

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
