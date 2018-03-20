from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from .task import Task


class Zone(Task):
    # TODO: Migrate to .ui file using QtDesigner
    def __init__(self, zone_name, zone_type, parent=None):
        super().__init__(zone_name, zone_type, parent)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = Zone("Locker Area", "region")
    window.show()

    app.exec_()
