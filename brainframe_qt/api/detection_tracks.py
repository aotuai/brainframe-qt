from uuid import UUID
from typing import List, Tuple
from collections import deque

from brainframe.client.api import codecs


class DetectionTrack:
    def __init__(self, max_size=1000):
        """"""
        self._history = deque(maxlen=max_size)

    def __getitem__(self):
        """
        The 0th index in track should be the latest

        """

    def add_detection(self, detection, tstamp):
        """Pops the oldest (if len is > max size) and inserts the newest
        to the beginning of the list."""
        self._history.append((detection, tstamp))

    @property
    def class_name(self) -> str:
        """Get the class name for this detection"""
        if not len(self._history):
            raise IndexError("There are no detect")

    @property
    def track_id(self) -> UUID:
        """Get the track_id for this detection"""
