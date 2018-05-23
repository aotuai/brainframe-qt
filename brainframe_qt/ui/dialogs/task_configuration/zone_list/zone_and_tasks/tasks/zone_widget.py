from .task_widget import TaskWidget


class ZoneWidget(TaskWidget):
    # TODO(Bryce Beagle): Migrate to .ui file using QtDesigner
    def __init__(self, zone_name, zone_type, parent=None):
        super().__init__(zone_name, zone_type, parent)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = ZoneWidget("Locker Area", "region")
    window.show()

    app.exec_()
