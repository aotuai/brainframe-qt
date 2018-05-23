from PyQt5.QtWidgets import QTreeWidget


class TreeWidget(QTreeWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
