from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi


class AlarmCreationDialog(QDialog):

    def __init__(self, parent):

        super().__init__(parent)

        loadUi("ui/dialogs/alarm_creation/alarm_creation.ui", self)


if __name__ == '__main__':

    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = AlarmCreationDialog(None)
    window.show()

    app.exec_()
