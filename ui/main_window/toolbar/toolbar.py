from PyQt5.QtWidgets import QWidget


class Toolbar(QWidget):

    def __init__(self, parent):

        # Flags isn't required but PyCharm complains
        super().__init__(parent, flags=None)

