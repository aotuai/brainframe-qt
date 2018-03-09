from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView


class VideoSmall(QGraphicsView):

    def __init__(self, parent):

        super().__init__(parent)

        self.scene_ = QGraphicsScene()
        self.setScene(self.scene_)

