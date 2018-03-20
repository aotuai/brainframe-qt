from PyQt5.QtCore import pyqtProperty, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView


# TODO
# from [] import Stream


class StreamWidget(QGraphicsView):
    """Base widget that uses Stream object to get frames

    Makes use of a QTimer to get frames"""

    def __init__(self, frame_rate=30, parent=None):
        """Init StreamWidget object

        :param frame_rate: Frame rate of video in fps
        """
        super().__init__(parent)

        # TODO: Without caching this, UI gets laggy. This might be an issue
        self._pixmap_temp = QPixmap("ui/resources/video.jpeg").scaled(300, 200)

        self.scene_ = QGraphicsScene()
        self.setScene(self.scene_)

        self.video_stream = None  # TODO: Stream()
        self.current_frame = None

        self._frame_rate = frame_rate

        # Get first frame, then start timer to do it repetitively
        self.update_frame()
        self.frame_update_timer = QTimer()
        # noinspection PyUnresolvedReferences
        self.frame_update_timer.timeout.connect(self.update_frame)
        self.frame_update_timer.start(1000 // self.frame_rate)

    def update_frame(self):
        """Grab the newest frame from the Stream object"""

        # TODO: Use Stream frame
        # pixmap = QPixmap(self.video_stream.get_frame())
        self.current_frame = self.scene_.addPixmap(self._pixmap_temp)

    # TODO
    def change_stream(self, stream_id):
        """Change the stream source of the video

        If stream_id is None, the Widget will remove stop grabbing frames"""
        if stream_id is None:
            pass
        else:
            pass

    @pyqtProperty(int)
    def frame_rate(self):
        return self._frame_rate

    @frame_rate.setter
    def frame_rate(self, frame_rate):
        self.frame_update_timer.setInterval(1000 // frame_rate)
        self._frame_rate = frame_rate

