import typing

from PyQt5.QtCore import QObject
from brainframe.api import BrainFrameAPI

# Singleton API instance
api = BrainFrameAPI()

# Must come after api import
from .streaming import StreamManager

# Set using init_stream_manager before use
_stream_manager: StreamManager = typing.cast(StreamManager, None)


def init_stream_manager(*, parent: QObject) -> None:
    global _stream_manager
    _stream_manager = StreamManager(parent=parent)


def get_stream_manager() -> StreamManager:
    return _stream_manager
