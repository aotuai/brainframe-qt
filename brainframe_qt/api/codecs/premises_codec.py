from brainframe.client.api.codecs import Codec


class Premises(Codec):
    """Information about a specific Premises"""

    def __init__(self, *, name: str, id_=None):
        self.id = id_
        self.name = name

    def to_dict(self):
        d = dict(self.__dict__)
        return d

    @staticmethod
    def from_dict(d):
        return Premises(name=d["name"], id_=d["id"])
