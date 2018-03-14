from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi


class TaskConfiguration(QWidget):

    def __init__(self, parent):

        super().__init__(parent)

        loadUi("ui/dialogs/task_configuration/task_configuration.ui", self)
