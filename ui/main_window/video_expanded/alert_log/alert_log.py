from PyQt5.QtWidgets import QWidget


class AlertLog(QWidget):

    def __init__(self, parent):

        # Flags isn't required but PyCharm complains
        super().__init__(parent, flags=None)
