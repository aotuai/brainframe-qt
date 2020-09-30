import typing
from typing import List

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QColor, QPainterPath, QPolygonF
from PyQt5.QtWidgets import QGraphicsPathItem

from brainframe.client.api_utils.detection_tracks import DetectionTrack
from brainframe.client.ui.resources.video_items.base import VideoItem
from brainframe.client.ui.resources.video_items.stream_detection import \
    generate_unique_qcolor


class DetectionTrackItem(QGraphicsPathItem):
    MAX_TRACK_AGE = 10
    """Remove tracks over X seconds long"""
    LINE_THICKNESS = 2

    def __init__(self, track: DetectionTrack, *, parent: VideoItem):
        super().__init__(parent=parent)

        self._color = typing.cast(QColor, None)
        self._track = typing.cast(DetectionTrack, None)
        self.track = track

        self._thickness = typing.cast(int, None)
        self.thickness = self.LINE_THICKNESS

    @property
    def track(self) -> DetectionTrack:
        return self._track

    @track.setter
    def track(self, track: DetectionTrack):
        self._track = track
        self.color = generate_unique_qcolor(str(track.track_id))

        line_coords: List[QPointF] = []
        for prev_det, detection_tstamp in track:
            # Find the point of the detection closest to the screens bottom
            if track.latest_tstamp - detection_tstamp > self.MAX_TRACK_AGE:
                break
            coord_a, coord_b = sorted(prev_det.coords,
                                      key=lambda pt: -pt[1])[:2]

            # The midpoint will be the next point in our line
            midpoint = [(coord_a[0] + coord_b[0]) / 2,
                        (coord_a[1] + coord_b[1]) / 2]
            line_coords.append(QPointF(*midpoint))

        polygon = QPolygonF(line_coords)
        painter_path = QPainterPath()
        painter_path.addPolygon(polygon)

        self.setPath(painter_path)

    @property
    def color(self) -> QColor:
        return self._color

    @color.setter
    def color(self, color: QColor):
        self._color = color

        pen = self.pen()
        pen.setColor(color)

        self.setPen(pen)

    @property
    def thickness(self) -> int:
        return self._thickness

    @thickness.setter
    def thickness(self, thickness: int):
        self._thickness = thickness

        pen = self.pen()
        pen.setWidth(thickness)

        self.setPen(pen)
