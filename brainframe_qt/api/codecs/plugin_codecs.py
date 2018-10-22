from brainframe.shared import codec_enums
from brainframe.client.api.codecs import Codec


class PluginOption(Codec):
    """A single configuration option for a plugin. Defines what type of option
    it is, its potential values, and its current value.

    There are two kinds of plugin options. Stream plugin options apply only to
    the stream they are attached to. Global plugin options apply to all streams,
    but are overridden by stream plugin options.
    """
    OptionType = codec_enums.OptionType

    def __init__(self, *, type_, default, value, constraints):
        self.type = type_
        self.default = default
        self.value = value
        self.constraints = constraints

    def to_dict(self):
        d = dict(self.__dict__)
        d["type"] = self.type.value
        return d

    @staticmethod
    def from_dict(d):
        type_ = PluginOption.OptionType(d["type"])
        return PluginOption(type_=type_,
                            default=d["default"],
                            value=d["value"],
                            constraints=d["constraints"])
