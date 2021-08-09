import typing

from PyQt5.QtCore import QObject
from brainframe.api import BrainFrameAPI

# Singleton API instance
api = BrainFrameAPI()

# Must come after api import
from .streaming import StreamManager

# Set using init_stream_manager before use
#
# Note: Creating singleton QObjects is a bit of a hassle because they need a parent
# object. Flutter has a really cool system called InheritedWidget/Provider that makes
# passing objects like this around really easily. I'd like to implement something
# similar, but for now this is the only singleton object we have so I think this
# should be begrudgingly "ok".
_stream_manager: StreamManager = typing.cast(StreamManager, None)


def init_stream_manager(*, parent: QObject) -> None:
    global _stream_manager

    if _stream_manager is not None:
        raise RuntimeError("StreamManager has already been initialized")

    _stream_manager = StreamManager(parent=parent)


def get_stream_manager() -> StreamManager:
    if _stream_manager is None:
        raise RuntimeError(
            f"StreamManager has not been initialized yet. Call "
            f"{init_stream_manager.__name__} first."
        )

    return _stream_manager
