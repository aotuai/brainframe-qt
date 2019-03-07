from uuid import UUID
from typing import Tuple, Deque, Iterator
from collections import deque

import numpy as np

from brainframe.client.api.codecs import Detection

DET_TSTAMP_TUPLE = Tuple[Detection, float]


class DetectionTrack:
    def __init__(self, history=None, max_size=1000):
        self._max_size = max_size
        self._history: Deque[DET_TSTAMP_TUPLE]
        self._history = history if history else deque(maxlen=self._max_size)

    def __len__(self):
        return len(self._history)

    def __iter__(self) -> Iterator[DET_TSTAMP_TUPLE]:
        """
        The 0th index in track should be the latest

        """
        for item in self._history:
            yield item

    def __repr__(self):
        if len(self._history):
            return f"DetectionTrack(tstamp: {self.latest_tstamp}, " \
                f"det:{self.latest_det})"
        else:
            return "DetectionTrack()"

    def add_detection(self, detection, tstamp):
        """Pops the oldest (if len is > max size) and inserts the newest
        to the beginning of the list."""
        self._history.appendleft((detection, tstamp))

    def get_interpolated_detection(self, interp_to_tstamp) -> Detection:
        """
        Returns a Detection codec whose coordinates are between those of the
        detections at tstamp n-1 and n+1, where n is interpolate tstamp


        :param interpolate_to_tstamp: The timestamp that we would like to
        estimate the position of the detection at.
        """
        if len(self._history) == 1:
            return self._history[0][0]

        if interp_to_tstamp == self.latest_tstamp:
            return self.latest_det

        if interp_to_tstamp > self.latest_tstamp:
            raise ValueError("You can't interpolate to a timestamp that's "
                             "higher than the current tracks latest timestamp!")
        recent: DET_TSTAMP_TUPLE = None
        older: DET_TSTAMP_TUPLE = None
        for det, tstamp in self:
            if tstamp >= interp_to_tstamp:
                recent = det, tstamp
            else:
                older = det, tstamp
                break

        ratio = 1 - (recent[1] - interp_to_tstamp) / (recent[1] - older[1])

        newer_coords = np.array(recent[0].coords)
        older_coords = np.array(older[0].coords)
        interp_coords = older_coords + (newer_coords - older_coords) * ratio

        """
        The following things should be true (For debugging):
        assert recent[1] >= interp_to_tstamp >= older[1]
        assert 0 <= ratio <= 1, ratio
        assert recent[0] == self.latest_det
        """

        # Return a new Detection but the coordinates have been interpolated
        return Detection(
            coords=interp_coords.astype(np.int).tolist(),
            class_name=recent[0].class_name,
            children=recent[0].children,
            attributes=recent[0].attributes,
            with_identity=recent[0].with_identity,
            extra_data=recent[0].extra_data,
            track_id=recent[0].track_id)

    @property
    def class_name(self) -> str:
        """Get the class name for this detection"""
        return self._history[0][0].class_name

    @property
    def track_id(self) -> UUID:
        """Get the track_id for this detection"""
        return self._history[0][0].track_id

    @property
    def latest_tstamp(self) -> float:
        return self._history[0][1]

    @property
    def latest_det(self) -> Detection:
        return self._history[0][0]

    def copy(self) -> 'DetectionTrack':
        return DetectionTrack(
            max_size=self._max_size,
            history=self._history.copy())
