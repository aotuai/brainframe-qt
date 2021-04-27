from brainframe.api import BrainFrameAPI
from .streaming import StreamManager, StreamManagerAPI

# API instance that is later monkeypatched to be a singleton
api: BrainFrameAPI = StreamManagerAPI()
