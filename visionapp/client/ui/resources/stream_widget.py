# noinspection PyUnresolvedReferences
# pyqtProperty is erroneously detected as unresolved
from PyQt5.QtCore import pyqtProperty, Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView


# TODO
# from [] import Stream


class StreamWidget(QGraphicsView):
    """Base widget that uses Stream object to get frames

    Makes use of a QTimer to get frames"""

    def __init__(self, stream_conf=None, frame_rate=30, parent=None):
        """Init StreamWidget object

        :param frame_rate: Frame rate of video in fps
        """
        super().__init__(parent)

        self.stream_conf = None
        self.stream_id = None

        self.change_stream(stream_conf)

        self.scene_ = QGraphicsScene()
        self.setScene(self.scene_)

        self.video_stream = None  # TODO: StreamReader()
        self.current_frame = None

        self._frame_rate = frame_rate

        # Get first frame, then start timer to do it repetitively
        self.update_frame()
        self.frame_update_timer = QTimer()

        # noinspection PyUnresolvedReferences
        # .connect is erroneously detected as unresolved
        self.frame_update_timer.timeout.connect(self.update_frame)
        self.frame_update_timer.start(1000 // frame_rate)

    def update_frame(self):
        """Grab the newest frame from the Stream object"""

        # TODO: Use Stream frame
        # pixmap = QPixmap(self.video_stream.get_frame())
        if not self.current_frame:
            self.current_frame = self.scene_.addPixmap(self._pixmap_temp)
        else:
            self.current_frame.setPixmap(self._pixmap_temp)
        self.fitInView(self.current_frame)

    # TODO
    def change_stream(self, stream_conf):
        """Change the stream source of the video

        If stream_conf is None, the Widget will remove stop grabbing frames"""
        self.stream_conf = stream_conf
        self.stream_id = stream_conf.id if stream_conf else None

        # TODO: Without caching this, UI gets laggy. This might be an issue
        # It might also be because of the IO read. If the frame is from a video
        # object
        if stream_conf:
            self._pixmap_temp = QPixmap(str(stream_conf.parameters['path']))
        else:
            # TODO: Don't hardcode path
            self._pixmap_temp = QPixmap("ui/resources/images/video_not_found.png")

    @pyqtProperty(int)
    def frame_rate(self):
        return self._frame_rate

    @frame_rate.setter
    def frame_rate(self, frame_rate):
        self.frame_update_timer.setInterval(1000 // frame_rate)
        self._frame_rate = frame_rate

    def resizeEvent(self, event):
        self.fitInView(self.current_frame)
        super().resizeEvent(event)

